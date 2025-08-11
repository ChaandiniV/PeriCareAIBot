import streamlit as st
import os
from knowledge_base import PostpartumKnowledgeBase
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
        with st.spinner("Loading knowledge base..."):
            try:
                st.session_state.knowledge_base = PostpartumKnowledgeBase()
                st.session_state.knowledge_base.load_data()
                st.success("✅ Knowledge base loaded successfully!")
            except Exception as e:
                st.error(f"❌ Failed to load knowledge base: {str(e)}")
                st.info("Please check your Gemini API key and internet connection.")
                st.stop()
    
    # Initialize chat interface
    if "chat_interface" not in st.session_state:
        st.session_state.chat_interface = ChatInterface(st.session_state.knowledge_base)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    # Display structured response
                    if "content" in message:
                        st.markdown(message["content"])
                    if "metadata" in message:
                        metadata = message["metadata"]
                        if metadata.get("confidence_score"):
                            st.caption(f"Confidence: {metadata['confidence_score']:.2f}")
                        if metadata.get("related_questions"):
                            with st.expander("Related Questions"):
                                for rq in metadata["related_questions"]:
                                    st.write(f"• {rq}")
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
                        
                        # Display metadata
                        if metadata.get("confidence_score"):
                            st.caption(f"Confidence: {metadata['confidence_score']:.2f}")
                        
                        if metadata.get("related_questions"):
                            with st.expander("Related Questions"):
                                for rq in metadata["related_questions"]:
                                    st.write(f"• {rq}")
                        
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
