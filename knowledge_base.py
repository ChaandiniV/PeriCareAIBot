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
        """Search for relevant Q&A pairs - prioritize exact matches first, then keyword matching"""
        if not self.data:
            raise ValueError("Knowledge base not loaded. Call load_data() first.")
        
        # First try direct keyword matching for better results
        direct_results = self._fallback_search(query, top_k)
        
        # If we get good matches from keyword search, use those
        if direct_results and direct_results[0][1] > 0.7:
            return direct_results
        
        # Otherwise try Gemini search as backup
        try:
            # Use a more focused Gemini search
            search_prompt = f"""
            Find the question number that best matches: "{query}"
            
            Questions:
            """
            
            # Add questions with their index
            for i, item in enumerate(self.data):
                question = item.get("Question", "")
                keywords = item.get("Keywords", "")
                search_prompt += f"{i+1}. {question} (Keywords: {keywords})\n"
            
            search_prompt += f"""
            
            Return ONLY the question number (1-{len(self.data)}) that best matches the user's query.
            If multiple questions match, return the best one.
            Response format: just the number, like: 42
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=search_prompt
            )
            
            if response.text and response.text.strip().isdigit():
                question_num = int(response.text.strip()) - 1
                if 0 <= question_num < len(self.data):
                    return [(self.data[question_num], 0.8)]
            
        except Exception as e:
            print(f"Gemini search failed: {e}")
        
        # Return the keyword search results as final fallback
        return direct_results if direct_results else []
    
    def _fallback_search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Direct keyword and phrase matching search"""
        if not self.data:
            return []
        
        query_lower = query.lower()
        results = []
        
        for item in self.data:
            score = 0.0
            
            question = item.get("Question", "").lower()
            keywords = item.get("Keywords", "").lower()
            short_answer = item.get("Short Answer", "").lower()
            long_answer = item.get("Long Answer", "").lower()
            
            # Exact question match gets highest score
            if query_lower == question:
                score = 1.0
            # High score for questions containing the query or query containing the question
            elif query_lower in question or question in query_lower:
                score = 0.95
            else:
                # Check key phrases first
                key_phrases = [
                    "low milk supply", "milk supply", "pump at work", "pumping at work",
                    "postpartum bleeding", "hair loss", "c-section", "exercise after birth",
                    "breastfeeding", "stitches", "period return", "diastasis recti"
                ]
                
                for phrase in key_phrases:
                    if phrase in query_lower and phrase in (question + " " + keywords + " " + short_answer):
                        score = max(score, 0.9)
                
                # Check individual meaningful words
                query_words = [word for word in query_lower.split() if len(word) > 3]
                word_matches = 0
                
                for word in query_words:
                    if word in question:
                        score += 0.3
                        word_matches += 1
                    elif word in keywords:
                        score += 0.25
                        word_matches += 1
                    elif word in short_answer:
                        score += 0.15
                        word_matches += 1
                    elif word in long_answer:
                        score += 0.1
                
                # Boost score if multiple words match
                if word_matches >= 2:
                    score += 0.2
                
                # Check category match
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
    
    def generate_conversational_response(self, user_query: str, matched_data: Dict = None) -> str:
        """Generate a conversational response using Gemini"""
        try:
            if matched_data:
                # Create a conversational response based on matched data
                prompt = f"""
                You are a warm, supportive postpartum health assistant. A new mother asked: "{user_query}"
                
                Based on this information from our medical knowledge base:
                - Question: {matched_data.get('Question', '')}
                - Short Answer: {matched_data.get('Short Answer', '')}
                - Detailed Answer: {matched_data.get('Long Answer', '')}
                - When to Seek Help: {matched_data.get('When to Seek Help', '')}
                - Source: {matched_data.get('Source', '')}
                
                Please provide a warm, conversational response that:
                1. Is concise but supportive (2-3 sentences max)
                2. Incorporates the most important medical information from Short Answer and Long Answer
                3. Uses the tone: {matched_data.get('Tone', 'supportive, empathetic')}
                4. Feels like talking to a knowledgeable friend
                5. Keeps essential medical accuracy but brief and conversational
                
                Keep it short and helpful - don't repeat all the information, just the key points.
                """
            else:
                # Generate a general helpful response for questions not in the knowledge base
                prompt = f"""
                You are a warm, supportive postpartum health assistant. A new mother asked: "{user_query}"
                
                This question isn't directly covered in our knowledge base, but you should:
                1. Acknowledge her concern warmly
                2. Provide general supportive guidance if it's related to postpartum health
                3. Always emphasize consulting with healthcare providers for specific medical advice
                4. Be encouraging and supportive
                5. If it's completely unrelated to postpartum health, gently redirect to postpartum topics
                
                Keep the response conversational and caring, like talking to a supportive friend.
                """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "I'm here to help with any postpartum questions you have. Could you tell me more about what you're experiencing?"
            
        except Exception as e:
            print(f"Failed to generate conversational response: {e}")
            return "I'm here to support you through your postpartum journey. Could you help me understand what specific concern you have?"
    
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
