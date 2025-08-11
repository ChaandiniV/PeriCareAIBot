# Postpartum Health Assistant

## Overview

This is a Streamlit-based chatbot application designed to provide evidence-based information and support to new mothers during their postpartum recovery journey. The assistant leverages a comprehensive knowledge base of postpartum health information and uses OpenAI's GPT-4o model with LlamaIndex for intelligent question answering. The application covers various aspects of postpartum care including physical recovery, breastfeeding, emotional wellbeing, and provides clear guidance on when to seek professional medical help.

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
- OpenAI GPT-4o as the primary language model for response generation
- OpenAI embeddings for semantic search capabilities
- LlamaIndex framework for document indexing, retrieval, and query processing
- Vector-based search with confidence scoring and threshold filtering

**Data Management**
- JSON-based knowledge base containing structured Q&A pairs
- Document parsing and indexing system that creates comprehensive text representations
- Metadata preservation for categories, sources, and related questions
- Semantic search with top-k retrieval (default k=3)

**Response Generation System**
- Confidence-based response filtering (threshold: 0.6)
- Structured response formatting with short answers, detailed explanations, and related questions
- Fallback responses for low-confidence or failed queries
- Error handling with graceful degradation

## External Dependencies

**APIs and Services**
- OpenAI API: GPT-4o model for text generation and embeddings
- Requires OPENAI_API_KEY environment variable

**Python Libraries**
- `streamlit`: Web application framework
- `llama-index`: Document indexing and retrieval framework
- `pandas`: Data manipulation (imported but usage not shown in provided code)
- `openai`: OpenAI API client (via LlamaIndex)

**Data Sources**
- Static JSON knowledge base file: `attached_assets/postpartum_physical_recovery_1754936677091.json`
- Contains evidence-based postpartum health information with citations to medical sources (Mayo Clinic, NHS, Cleveland Clinic)

**Configuration Requirements**
- OpenAI API key must be set as environment variable
- Knowledge base JSON file must be present in the attached_assets directory
- Internet connection required for OpenAI API calls