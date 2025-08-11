import json
import os
import pandas as pd
from typing import List, Dict, Tuple, Optional
from google import genai
from google.genai import types
import streamlit as st

class PostpartumKnowledgeBase:
    def __init__(self):
        # Note that the newest Gemini model series is "gemini-2.5-flash" or "gemini-2.5-pro"
        # This API key is from Gemini Developer API Key, not vertex AI API Key
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=self.gemini_api_key)
        
        self.data = None
        
    def load_data(self):
        """Load and process the JSON knowledge base"""
        try:
            # Load the JSON file
            with open("attached_assets/postpartum_physical_recovery_1754936677091.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
            
            print(f"✅ Loaded {len(self.data)} Q&A pairs into knowledge base")
            
        except FileNotFoundError:
            raise FileNotFoundError("Knowledge base JSON file not found. Please ensure the file is available.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise Exception(f"Failed to load knowledge base: {e}")
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Search for relevant Q&A pairs using Gemini for intelligent matching"""
        if not self.data:
            raise ValueError("Knowledge base not loaded. Call load_data() first.")
        
        try:
            # Use Gemini to find the best matching questions
            search_prompt = f"""
            You are helping to find the most relevant postpartum health questions for a user's query.
            
            User's question: "{query}"
            
            Available questions and their keywords:
            """
            
            # Add all questions with their keywords for context
            for i, item in enumerate(self.data):
                question = item.get("Question", "")
                keywords = item.get("Keywords", "")
                category = item.get("Category", "")
                search_prompt += f"\n{i+1}. {question} (Keywords: {keywords}, Category: {category})"
            
            search_prompt += f"""
            
            Please return the top {top_k} most relevant question numbers (1-{len(self.data)}) that best match the user's query.
            Also provide a confidence score from 0.0 to 1.0 for each match.
            
            Respond in this exact JSON format:
            {{"matches": [{{"question_number": 1, "confidence": 0.95}}, {{"question_number": 5, "confidence": 0.8}}]}}
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=search_prompt
            )
            
            if not response.text:
                return []
            
            # Parse the response
            import json
            try:
                result = json.loads(response.text)
                matches = result.get("matches", [])
                
                results = []
                for match in matches[:top_k]:
                    question_num = match.get("question_number", 1) - 1  # Convert to 0-based index
                    confidence = match.get("confidence", 0.0)
                    
                    if 0 <= question_num < len(self.data):
                        results.append((self.data[question_num], confidence))
                
                return results
                
            except json.JSONDecodeError:
                # Fallback to simple keyword matching
                return self._fallback_search(query, top_k)
            
        except Exception as e:
            print(f"Gemini search failed: {e}")
            # Fallback to simple keyword matching
            return self._fallback_search(query, top_k)
    
    def _fallback_search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Fallback search using simple keyword matching"""
        if not self.data:
            return []
        
        query_lower = query.lower()
        results = []
        
        for item in self.data:
            score = 0.0
            
            # Check question
            question = item.get("Question", "").lower()
            if query_lower in question:
                score += 0.8
            
            # Check keywords
            keywords = item.get("Keywords", "").lower()
            query_words = query_lower.split()
            for word in query_words:
                if word in keywords:
                    score += 0.3
                if word in question:
                    score += 0.2
            
            # Check category
            category = item.get("Category", "").lower()
            if any(word in category for word in query_words):
                score += 0.1
            
            if score > 0:
                results.append((item, min(score, 1.0)))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_best_match(self, query: str, confidence_threshold: float = 0.6) -> Optional[Tuple[Dict, float]]:
        """Get the best matching Q&A pair with confidence filtering"""
        results = self.search(query, top_k=1)
        
        if not results:
            return None
        
        best_match, confidence = results[0]
        
        # Apply confidence threshold
        if confidence < confidence_threshold:
            return None
        
        return best_match, confidence
    
    def get_categories(self) -> List[str]:
        """Get list of available categories"""
        if not self.data:
            return []
        
        categories = set()
        for item in self.data:
            if item.get("Category"):
                categories.add(item["Category"])
        
        return sorted(list(categories))
    
    def get_questions_by_category(self, category: str) -> List[Dict]:
        """Get all questions in a specific category"""
        if not self.data:
            return []
        
        return [item for item in self.data if item.get("Category", "").lower() == category.lower()]
