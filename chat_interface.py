import re
from typing import Tuple, Dict, Any
import streamlit as st

class ChatInterface:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
        self.confidence_threshold = 0.6
        
    def get_response(self, user_question: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a response to user's question"""
        try:
            # Search for relevant information
            results = self.knowledge_base.search(user_question, top_k=3)
            
            if not results:
                return self._get_fallback_response(), {"confidence_score": 0.0}
            
            # Get the best match
            best_match, confidence = results[0]
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                return self._get_fallback_response(), {"confidence_score": confidence}
            
            # Format the response
            response = self._format_response(best_match)
            
            # Prepare metadata
            metadata = {
                "confidence_score": confidence,
                "category": best_match.get("Category", ""),
                "source": best_match.get("Source", ""),
                "related_questions": self._parse_related_questions(best_match.get("Related Questions", ""))
            }
            
            return response, metadata
            
        except Exception as e:
            error_response = (
                "I'm sorry, I encountered an error while searching for information. "
                "Please try rephrasing your question or consult with a healthcare provider."
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
