# Postpartum Health Assistant 🤱

An AI-powered chatbot that provides evidence-based information and support to new mothers during their postpartum recovery journey. The assistant covers 8 categories of postpartum care including physical recovery, breastfeeding, emotional health, newborn care, and more.

## Features

- **Comprehensive Knowledge Base**: 113+ Q&A pairs covering all aspects of postpartum health
- **Intelligent Search**: Enhanced search system that finds exact answers from the knowledge base
- **Conversational AI**: Warm, supportive responses using Google Gemini AI
- **Evidence-Based**: Information sourced from trusted medical sources (Mayo Clinic, NHS, Cleveland Clinic)
- **User-Friendly**: Clean Streamlit interface with clickable related questions

## Categories Covered

- Physical Recovery
- Breastfeeding Basics & Common Issues
- Emotional & Mental Health
- Lifestyle & Daily Life
- Newborn Care
- Pumping & Storage
- Sexual & Reproductive Health

## Setup for Local Development

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Gemini API key:
   - Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set it as an environment variable: `GEMINI_API_KEY=your_key_here`
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment on Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set `app.py` as the main file
5. Add your `GEMINI_API_KEY` in the Secrets section
6. Deploy!

## Important Notes

⚠️ **Medical Disclaimer**: This tool provides general information only. Always consult with healthcare professionals for medical advice, diagnosis, or treatment.

## Data Sources

Information is sourced from trusted medical organizations including:
- Mayo Clinic
- NHS (National Health Service)
- Cleveland Clinic
- American Academy of Pediatrics
- WHO (World Health Organization)
- CDC (Centers for Disease Control)