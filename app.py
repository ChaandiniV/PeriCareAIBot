import streamlit as st
import os
from rag_system import PostpartumRAGSystem
from chat_interface import ChatInterface

# Configure Streamlit page
st.set_page_config(
    page_title="Postpartum Health Assistant",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    st.title("🤱 Postpartum Health Assistant")
    st.markdown(
        """
        Welcome to your postpartum health companion! Ask questions about physical recovery, 
        breastfeeding, emotional wellbeing, and more. This assistant provides evidence-based 
        information to support you during your postpartum journey.
        
        **⚠️ Important:** This tool provides general information only. Always consult with 
        healthcare professionals for medical advice, diagnosis, or treatment.
        """
    )
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "knowledge_base" not in st.session_state:
        with st.spinner("Loading RAG system..."):
            try:
                gemini_key = os.environ.get("GEMINI_API_KEY")
                openai_key = os.environ.get("OPENAI_API_KEY")  # Optional for better embeddings
                
                if not gemini_key:
                    st.error("❌ GEMINI_API_KEY not found in environment variables.")
                    st.stop()
                
                st.session_state.knowledge_base = PostpartumRAGSystem(gemini_key, openai_key)
                st.session_state.knowledge_base.load_knowledge_base("attached_assets/postpartum_physical_recovery_1754936677091.json")
                st.success("✅ RAG system loaded successfully!")
            except Exception as e:
                st.error(f"❌ Failed to load RAG system: {str(e)}")
                st.info("Please check your API keys and internet connection.")
                st.stop()
    
    # Initialize chat interface
    if "chat_interface" not in st.session_state:
        st.session_state.chat_interface = ChatInterface(st.session_state.knowledge_base)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    # Display response content
                    if "content" in message:
                        st.markdown(message["content"])
                    
                    if "metadata" in message:
                        metadata = message["metadata"]
                        
                        # Display additional info for knowledge base matches
                        if not metadata.get("conversational") or metadata.get("when_to_seek_help"):
                            if metadata.get("when_to_seek_help"):
                                st.warning(f"⚠️ **When to seek help:** {metadata['when_to_seek_help']}")
                        
                        # Display confidence and source
                        if metadata.get("confidence_score") and metadata["confidence_score"] > 0:
                            st.caption(f"Match confidence: {metadata['confidence_score']:.2f}")
                        
                        if metadata.get("source"):
                            source = metadata["source"]
                            if "http" in source:
                                import re
                                url_match = re.search(r'https?://[^\s]+', source)
                                if url_match:
                                    url = url_match.group()
                                    source_name = source.replace(url, "").replace("–", "").strip()
                                    st.caption(f"📚 Source: [{source_name}]({url})")
                                else:
                                    st.caption(f"📚 Source: {source}")
                            else:
                                st.caption(f"📚 Source: {source}")
                        
                        # Display clickable related questions
                        if metadata.get("related_questions"):
                            with st.expander("💡 You might also ask..."):
                                for j, rq in enumerate(metadata["related_questions"]):
                                    if st.button(rq, key=f"history_related_{i}_{j}", use_container_width=True):
                                        # Add the related question as if user typed it
                                        st.session_state.messages.append({"role": "user", "content": rq})
                                        st.rerun()
                else:
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about postpartum health..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get assistant response
            with st.chat_message("assistant"):
                with st.spinner("Searching for relevant information..."):
                    try:
                        response, metadata = st.session_state.chat_interface.get_response(prompt)
                        
                        # Display response
                        st.markdown(response)
                        
                        # Display additional info for knowledge base matches
                        if not metadata.get("conversational") or metadata.get("when_to_seek_help"):
                            if metadata.get("when_to_seek_help"):
                                st.warning(f"⚠️ **When to seek help:** {metadata['when_to_seek_help']}")
                        
                        # Display metadata
                        if metadata.get("confidence_score") and metadata["confidence_score"] > 0:
                            st.caption(f"Match confidence: {metadata['confidence_score']:.2f}")
                        
                        # Display source
                        if metadata.get("source"):
                            source = metadata["source"]
                            if "http" in source:
                                # Extract URL and source name
                                import re
                                url_match = re.search(r'https?://[^\s]+', source)
                                if url_match:
                                    url = url_match.group()
                                    source_name = source.replace(url, "").replace("–", "").strip()
                                    st.caption(f"📚 Source: [{source_name}]({url})")
                                else:
                                    st.caption(f"📚 Source: {source}")
                            else:
                                st.caption(f"📚 Source: {source}")
                        
                        # Display clickable related questions
                        if metadata.get("related_questions"):
                            with st.expander("💡 You might also ask..."):
                                for rq in metadata["related_questions"]:
                                    if st.button(rq, key=f"related_{rq}", use_container_width=True):
                                        # Add the related question as if user typed it
                                        st.session_state.messages.append({"role": "user", "content": rq})
                                        st.rerun()
                        
                        # Add assistant message to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response,
                            "metadata": metadata
                        })
                        
                    except Exception as e:
                        error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown(
            """
            This assistant uses evidence-based information from trusted medical sources 
            including:
            
            • Mayo Clinic
            • NHS (National Health Service)
            • Cleveland Clinic
            • American Academy of Pediatrics
            • WHO (World Health Organization)
            • CDC (Centers for Disease Control)
            
            **Coverage areas:**
            • Physical Recovery
            • Breastfeeding Support
            • Mental Health & Emotional Wellbeing
            • Baby Care & Development
            • Nutrition & Lifestyle
            """
        )
        
        st.header("🚨 Emergency Information")
        st.error(
            """
            **Seek immediate medical attention if you experience:**
            
            • Heavy bleeding (soaking a pad in under an hour)
            • Signs of infection (fever, chills, foul-smelling discharge)
            • Severe headaches or vision changes
            • Chest pain or difficulty breathing
            • Thoughts of harming yourself or your baby
            • Severe abdominal pain
            
            **Emergency contacts:**
            • Emergency services: 911 (US) / 999 (UK)
            • Postpartum Support International: 1-944-4-WARMLINE
            """
        )
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()
