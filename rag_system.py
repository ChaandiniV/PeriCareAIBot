"""
Enhanced search system for postpartum health knowledge base
"""
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from google import genai
import logging
import re

class PostpartumRAGSystem:
    def __init__(self, gemini_api_key: str, openai_api_key: Optional[str] = None):
        """Initialize the enhanced search system"""
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.knowledge_data = []
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_knowledge_base(self, json_file_path: str):
        """Load the knowledge base from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                self.knowledge_data = json.load(file)
            
            self.logger.info(f"✅ Loaded {len(self.knowledge_data)} Q&A pairs for enhanced search")
            
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            raise
    
    def _create_document_text(self, item: Dict) -> str:
        """Create a comprehensive text representation for better search"""
        text_parts = []
        
        # Add question (most important for matching)
        question = item.get('Question', '')
        if question:
            text_parts.append(f"Question: {question}")
        
        # Add category for context
        category = item.get('Category', '')
        if category:
            text_parts.append(f"Category: {category}")
        
        # Add keywords for better matching
        keywords = item.get('Keywords', '')
        if keywords:
            text_parts.append(f"Keywords: {keywords}")
        
        # Add short answer
        short_answer = item.get('Short Answer', '')
        if short_answer:
            text_parts.append(f"Short Answer: {short_answer}")
        
        # Add long answer
        long_answer = item.get('Long Answer', '')
        if long_answer:
            text_parts.append(f"Detailed Answer: {long_answer}")
        
        # Add when to seek help
        when_to_seek_help = item.get('When to Seek Help', '')
        if when_to_seek_help:
            text_parts.append(f"When to Seek Help: {when_to_seek_help}")
        
        return '\n\n'.join(text_parts)
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Search for relevant answers using enhanced keyword matching and AI assistance"""
        if not self.knowledge_data:
            raise ValueError("Knowledge base not loaded. Call load_knowledge_base() first.")
        
        # Use enhanced keyword search with AI assistance
        return self._enhanced_search(query, top_k)
    
    def _enhanced_search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Enhanced search using both keyword matching and AI assistance"""
        if not self.knowledge_data:
            return []
        
        query_lower = query.lower()
        results = []
        
        # Step 1: Direct keyword matching with high precision
        for item in self.knowledge_data:
            score = 0.0
            
            question = item.get("Question", "").lower()
            keywords = item.get("Keywords", "").lower()
            short_answer = item.get("Short Answer", "").lower()
            long_answer = item.get("Long Answer", "").lower()
            category = item.get("Category", "").lower()
            
            # Check for exact question match first (highest priority)
            if query_lower == question:
                score = 2.0  # Exact match gets highest score
            # Check for direct containment matches
            elif query_lower in question:
                score = 1.8  # User query is contained in the question
            elif question in query_lower:
                score = 1.6  # Question is contained in user query
            # Check for specific keyword matches
            elif "low milk supply" in query_lower and "low supply" in keywords:
                score = 1.5  # Specific low milk supply match
            # Check for other phrase matches
            else:
                key_phrases = [
                    "low milk supply", "milk supply", "pump at work", "pumping at work",
                    "postpartum bleeding", "hair loss", "c-section", "exercise after birth",
                    "breastfeeding", "stitches", "period return", "diastasis recti",
                    "night sweats", "hemorrhoids", "constipation", "perineal pain"
                ]
                
                # Phrase matching gets high score, but be more specific
                for phrase in key_phrases:
                    if phrase in query_lower:
                        # Exact phrase match in question gets highest score
                        if phrase in question:
                            score = max(score, 0.94)
                        # Phrase match in keywords gets good score
                        elif phrase in keywords:
                            score = max(score, 0.90)
                        # Phrase match in answers gets medium score
                        elif phrase in short_answer:
                            score = max(score, 0.86)
                        elif phrase in long_answer:
                            score = max(score, 0.82)
                
                # Word matching with context
                query_words = [word for word in query_lower.split() if len(word) > 3]
                word_matches = 0
                important_words = ["supply", "milk", "pump", "work", "bleeding", "exercise", "pain", "stitches"]
                
                for word in query_words:
                    if word in question:
                        if word in important_words:
                            score += 0.4
                        else:
                            score += 0.3
                        word_matches += 1
                    elif word in keywords:
                        score += 0.25
                        word_matches += 1
                    elif word in short_answer:
                        score += 0.15
                        word_matches += 1
                    elif word in category:
                        score += 0.1
                
                # Boost for multiple word matches
                if word_matches >= 2:
                    score += 0.15
                elif word_matches >= 3:
                    score += 0.25
            
            if score > 0:
                results.append((item, score))  # Don't cap scores, let natural ranking work
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Step 2: If no good matches, try AI-assisted matching
        if not results or (results and results[0][1] < 0.7):
            ai_results = self._ai_assisted_search(query, top_k)
            if ai_results:
                # Combine results, preferring high-confidence direct matches
                combined = {}
                for item, score in results[:top_k]:
                    item_key = item.get("Question", "")
                    combined[item_key] = (item, score)
                
                for item, ai_score in ai_results:
                    item_key = item.get("Question", "")
                    if item_key in combined:
                        # Use higher score
                        existing_score = combined[item_key][1]
                        combined[item_key] = (item, max(existing_score, ai_score))
                    else:
                        combined[item_key] = (item, ai_score)
                
                # Return top results
                final_results = list(combined.values())
                final_results.sort(key=lambda x: x[1], reverse=True)
                return final_results[:top_k]
        
        return results[:top_k]
    
    def _ai_assisted_search(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """Use Gemini to help find relevant questions"""
        try:
            # Create a prompt for Gemini to find matching questions
            questions_text = ""
            for i, item in enumerate(self.knowledge_data):
                questions_text += f"{i+1}. {item.get('Question', '')} (Keywords: {item.get('Keywords', '')})\n"
            
            prompt = f"""
            Find the {top_k} most relevant questions for: "{query}"
            
            Questions:
            {questions_text}
            
            Return only the question numbers (e.g., 1, 5, 23) that best match the user's query about postpartum health.
            Focus on questions that directly address the user's concern.
            Format: just the numbers separated by commas, like: 5, 12, 8
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response.text:
                # Parse the response to get question numbers
                numbers = re.findall(r'\d+', response.text)
                results = []
                
                for num_str in numbers[:top_k]:
                    try:
                        idx = int(num_str) - 1  # Convert to 0-based index
                        if 0 <= idx < len(self.knowledge_data):
                            results.append((self.knowledge_data[idx], 0.75))  # AI match confidence
                    except ValueError:
                        continue
                
                return results
            
        except Exception as e:
            self.logger.error(f"AI-assisted search failed: {e}")
        
        return []
    
    def generate_conversational_response(self, user_question: str, context_item: Optional[Dict] = None) -> str:
        """Generate a conversational response using Gemini"""
        try:
            if context_item:
                # Use the knowledge base item as context
                prompt = f"""
                You are a warm, supportive postpartum health assistant. A new mother asked: "{user_question}"

                Here's relevant information from our knowledge base:
                
                Question: {context_item.get('Question', '')}
                Short Answer: {context_item.get('Short Answer', '')}
                Detailed Answer: {context_item.get('Long Answer', '')}
                When to Seek Help: {context_item.get('When to Seek Help', '')}
                
                Please provide a warm, conversational response that incorporates this information. Be supportive and encouraging. Keep it concise but helpful.
                """
            else:
                # General conversational response
                prompt = f"""
                You are a warm, supportive postpartum health assistant. A new mother asked: "{user_question}"
                
                Provide a helpful, encouraging response about postpartum health. If you're not sure about specific medical advice, suggest consulting with healthcare providers. Keep it warm and supportive.
                """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "I'm here to help with any postpartum questions you have. Could you tell me more about what you're experiencing?"
            
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return "I understand you're looking for support. Please feel free to ask any questions about your postpartum recovery, and I'll do my best to help."