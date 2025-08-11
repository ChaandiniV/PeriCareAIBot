import re
from typing import Tuple, Dict, Any
import streamlit as st

class ChatInterface:
    def __init__(self, rag_system):
        self.rag_system = rag_system
        self.confidence_threshold = 0.6
        
    def get_response(self, user_question: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a response to user's question"""
        try:
            # Search for relevant information using RAG
            results = self.rag_system.search(user_question, top_k=3)
            
            if not results:
                # Use Gemini to generate a conversational response for questions not in knowledge base
                response = self.rag_system.generate_conversational_response(user_question)
                return response, {"confidence_score": 0.0, "conversational": True}
            
            # Get the best match
            best_match, confidence = results[0]
            
            # If we have a good match (0.7+), use the structured answer format
            if confidence >= 0.7:
                response = self._format_response(best_match)
            # For medium confidence (0.3-0.7), use conversational response with matched data
            elif confidence >= 0.3:
                response = self.rag_system.generate_conversational_response(user_question, best_match)
            # For low confidence, generate a general conversational response
            else:
                response = self.rag_system.generate_conversational_response(user_question)
                return response, {"confidence_score": confidence, "conversational": True}
            
            # Prepare metadata
            metadata = {
                "confidence_score": confidence,
                "category": best_match.get("Category", ""),
                "source": best_match.get("Source", ""),
                "related_questions": self._parse_related_questions(best_match.get("Related Questions", "")),
                "when_to_seek_help": best_match.get("When to Seek Help", ""),
                "conversational": confidence < 0.7  # Mark as conversational only for lower confidence
            }
            
            return response, metadata
            
        except Exception as e:
            error_response = (
                "I'm here to help with your postpartum journey. Could you tell me more about "
                "what you're experiencing? If you have urgent concerns, please don't hesitate "
                "to contact your healthcare provider."
            )
            return error_response, {"error": str(e)}
    
    def _format_response(self, match_data: Dict) -> str:
        """Format the response in a structured way"""
        response_parts = []
        
        # Short answer
        if match_data.get("Short Answer"):
            response_parts.append(f"**Quick Answer:** {match_data['Short Answer']}")
        
        # Long answer
        if match_data.get("Long Answer"):
            response_parts.append(f"**Detailed Information:** {match_data['Long Answer']}")
        
        # When to seek help
        if match_data.get("When to Seek Help"):
            response_parts.append(f"**⚠️ When to Seek Medical Help:** {match_data['When to Seek Help']}")
        
        # Source
        if match_data.get("Source"):
            source = match_data["Source"]
            # Extract URL if present
            url_match = re.search(r'https?://[^\s]+', source)
            if url_match:
                url = url_match.group()
                source_name = source.replace(url, "").replace("–", "").strip()
                response_parts.append(f"**📚 Source:** [{source_name}]({url})")
            else:
                response_parts.append(f"**📚 Source:** {source}")
        
        # Category
        if match_data.get("Category"):
            response_parts.append(f"**📂 Category:** {match_data['Category']}")
        
        return "\n\n".join(response_parts)
    
    def _parse_related_questions(self, related_questions_str: str) -> list:
        """Parse the related questions string into a list"""
        if not related_questions_str:
            return []
        
        # Split by semicolon and clean up
        questions = [q.strip() for q in related_questions_str.split(';') if q.strip()]
        return questions[:5]  # Limit to 5 related questions
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when no good match is found"""
        return (
            "I'm not certain about that specific question. For the most accurate and "
            "personalized guidance regarding your postpartum health, it's best to consult "
            "with your healthcare provider.\n\n"
            "**In the meantime, here are some general resources:**\n"
            "• Contact your OB/GYN or midwife\n"
            "• Call your hospital's postpartum support line\n"
            "• Reach out to Postpartum Support International: 1-944-4-WARMLINE\n\n"
            "**For emergencies:** If you're experiencing severe symptoms, please contact "
            "emergency services immediately (911 in the US, 999 in the UK)."
        )
    
    def get_suggested_questions(self) -> list:
        """Get a list of suggested questions to help users get started"""
        return [
            "How long will postpartum bleeding last?",
            "When can I start exercising again after birth?",
            "How do I care for a C-section incision?",
            "Is it normal to still look pregnant weeks after birth?",
            "How can I manage postpartum hair loss?",
            "What is diastasis recti and how do I treat it?",
            "How do I manage postpartum constipation?",
            "Which painkillers are safe while breastfeeding?",
            "How much postpartum swelling is normal?",
            "When will my period return after childbirth?"
        ]
    
    def format_emergency_info(self) -> str:
        """Format emergency information"""
        return (
            "**🚨 Seek immediate medical attention if you experience:**\n\n"
            "• Heavy bleeding (soaking a pad in under an hour)\n"
            "• Large blood clots\n"
            "• Signs of infection (fever, chills, foul-smelling discharge)\n"
            "• Severe headaches or vision changes\n"
            "• Chest pain or difficulty breathing\n"
            "• Thoughts of harming yourself or your baby\n"
            "• Severe abdominal pain\n"
            "• Leg swelling with redness or warmth\n\n"
            "**Emergency contacts:**\n"
            "• Emergency services: 911 (US) / 999 (UK)\n"
            "• Postpartum Support International: 1-944-4-WARMLINE"
        )
