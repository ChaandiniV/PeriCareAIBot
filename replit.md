# Postpartum Health Assistant

## Overview

This is a Streamlit-based chatbot application designed to provide evidence-based information and support to new mothers during their postpartum recovery journey. The assistant leverages a comprehensive knowledge base of postpartum health information and uses Google's Gemini AI for intelligent question answering and conversational responses. The application covers 8 categories of postpartum care: Physical Recovery, Breastfeeding Basics, Breastfeeding Common Issues, Emotional & Mental Health, Lifestyle & Daily Life, Newborn Care, Pumping & Storage, and Sexual & Reproductive Health.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture**
- Built with Streamlit for a clean, user-friendly web interface
- Single-page application with chat-based interaction model
- Session state management for maintaining conversation history and loaded components
- Real-time loading indicators and error handling for better user experience

**Backend Architecture**
- Modular Python application with three main components:
  - `app.py`: Main application entry point and Streamlit configuration
  - `knowledge_base.py`: Data processing and retrieval system using LlamaIndex
  - `chat_interface.py`: Chat logic and response formatting

**AI/ML Stack**
- Google Gemini 2.5-flash as the primary language model for intelligent search and conversational response generation
- Gemini-powered semantic search for matching user queries to knowledge base content
- Conversational AI that provides warm, supportive responses rather than clinical answers
- Fallback keyword-based search for reliability

**Data Management**
- JSON-based knowledge base containing structured Q&A pairs
- Document parsing and indexing system that creates comprehensive text representations
- Metadata preservation for categories, sources, and related questions
- Semantic search with top-k retrieval (default k=3)

**Response Generation System**
- Conversational AI responses using Gemini for warm, supportive communication
- Clickable related questions for enhanced user interaction
- Adaptive confidence thresholds (lowered to 0.3) for broader question coverage
- Intelligent fallback to conversational responses for any postpartum-related query
- Enhanced UI with warning callouts for "when to seek help" information

## External Dependencies

**APIs and Services**
- Google Gemini API: 2.5-flash model for intelligent search and conversational responses
- Requires GEMINI_API_KEY environment variable

**Python Libraries**
- `streamlit`: Web application framework
- `google-genai`: Google Gemini API client for AI capabilities
- `pandas`: Data manipulation utilities
- `typing`: Type hints for better code structure

**Data Sources**
- Static JSON knowledge base file: `attached_assets/postpartum_physical_recovery_1754936677091.json`
- Contains evidence-based postpartum health information with citations to medical sources (Mayo Clinic, NHS, Cleveland Clinic)

**Configuration Requirements**
- OpenAI API key must be set as environment variable
- Knowledge base JSON file must be present in the attached_assets directory
- Internet connection required for OpenAI API calls