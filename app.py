# app.py
import os
import re
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="MeetSumm AI - Meeting Notes Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    :root {
        --primary: #4361ee;
        --secondary: #3f37c9;
        --accent: #4895ef;
        --light: #f8f9fa;
        --dark: #212529;
        --success: #4cc9f0;
        --warning: #f72585;
        --gray: #6c757d;
        --light-gray: #e9ecef;
        --border-radius: 12px;
        --box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        --transition: all 0.3s ease;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
        background-attachment: fixed;
    }
    
    .header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        border-radius: var(--border-radius);
        color: white;
        box-shadow: var(--box-shadow);
    }
    
    .header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--box-shadow);
        margin-bottom: 1.5rem;
        transition: var(--transition);
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .card h2 {
        color: var(--primary);
        border-bottom: 2px solid var(--light-gray);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .btn-primary {
        background: var(--primary);
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 50px;
        font-weight: bold;
        cursor: pointer;
        transition: var(--transition);
        width: 100%;
        margin-top: 1rem;
    }
    
    .btn-primary:hover {
        background: var(--secondary);
        transform: scale(1.03);
    }
    
    .btn-secondary {
        background: var(--accent);
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 50px;
        font-weight: bold;
        cursor: pointer;
        transition: var(--transition);
        width: 100%;
        margin-top: 1rem;
    }
    
    .btn-secondary:hover {
        background: var(--secondary);
        transform: scale(1.03);
    }
    
    .summary-output {
        background: var(--light);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        min-height: 300px;
        border: 1px solid var(--light-gray);
    }
    
    .model-selector {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .model-option {
        flex: 1;
        padding: 1rem;
        border: 2px solid var(--light-gray);
        border-radius: var(--border-radius);
        text-align: center;
        cursor: pointer;
        transition: var(--transition);
    }
    
    .model-option:hover {
        border-color: var(--accent);
    }
    
    .model-option.selected {
        border-color: var(--primary);
        background: rgba(67, 97, 238, 0.1);
    }
    
    .model-option h3 {
        margin: 0;
        font-size: 1rem;
    }
    
    .model-option p {
        font-size: 0.85rem;
        color: var(--gray);
        margin: 0.5rem 0 0;
    }
    
    .tag {
        display: inline-block;
        background: var(--accent);
        color: white;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 1rem;
    }
    
    .status-processing {
        background: #ffcc00;
        color: #333;
    }
    
    .status-success {
        background: #4caf50;
        color: white;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--box-shadow);
        transition: var(--transition);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-card i {
        font-size: 2.5rem;
        color: var(--primary);
        margin-bottom: 1rem;
    }
    
    .feature-card h3 {
        margin: 0 0 0.5rem;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        color: var(--gray);
        font-size: 0.9rem;
        border-top: 1px solid var(--light-gray);
    }
    
    @media (max-width: 768px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }
        
        .model-selector {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'custom_prompt' not in st.session_state:
    st.session_state.custom_prompt = "Summarize the key points in bullet format"
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'edited_summary' not in st.session_state:
    st.session_state.edited_summary = ""
if 'model' not in st.session_state:
    st.session_state.model = "llama3-70b-8192"
if 'email_sent' not in st.session_state:
    st.session_state.email_sent = False
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Header section
st.markdown("""
<div class="header">
    <h1><i class="fas fa-file-alt"></i> MeetSumm AI</h1>
    <p>AI-Powered Meeting Notes Summarizer & Sharer</p>
</div>
""", unsafe_allow_html=True)

# Main columns
col1, col2 = st.columns([1, 1], gap="large")

# Input Section
with col1:
    st.markdown('<div class="card"><h2><i class="fas fa-upload"></i> Upload Meeting Notes</h2></div>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
    if uploaded_file is not None:
        st.session_state.transcript = uploaded_file.read().decode("utf-8")
    
    # Text area for transcript
    st.markdown('<div class="card"><h3>Or paste your meeting notes:</h3></div>', unsafe_allow_html=True)
    transcript_text = st.text_area("", st.session_state.transcript, height=250, 
                                  placeholder="Paste meeting transcript here...")
    st.session_state.transcript = transcript_text
    
    # Custom instruction input
    st.markdown('<div class="card"><h2><i class="fas fa-sliders-h"></i> Custom Instructions</h2></div>', unsafe_allow_html=True)
    custom_prompt = st.text_area("How should we summarize?", st.session_state.custom_prompt, height=100,
                                placeholder="e.g., 'Summarize in bullet points for executives' or 'Highlight only action items'")
    st.session_state.custom_prompt = custom_prompt
    
    # Model selection
    st.markdown('<div class="card"><h2><i class="fas fa-brain"></i> AI Model</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="model-selector">', unsafe_allow_html=True)
    
    models = {
        "llama3-70b-8192": {"name": "Llama 3 70B", "desc": "Most powerful", "context": "8K tokens"},
        "gemma-7b-it": {"name": "Gemma 7B", "desc": "Lightweight & fast", "context": "8K tokens"}
    }
    
    cols = st.columns(3)
    for i, (model_id, model_info) in enumerate(models.items()):
        with cols[i]:
            selected = st.session_state.model == model_id
            st.markdown(f"""
            <div class="model-option {'selected' if selected else ''}" onclick="selectModel('{model_id}')">
                <h3>{model_info['name']}</h3>
                <p>{model_info['desc']}</p>
                <small>{model_info['context']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate button
    if st.button("Generate Summary", use_container_width=True, type="primary"):
        if not st.session_state.transcript.strip():
            st.warning("Please enter meeting notes or upload a file")
        else:
            st.session_state.processing = True
            try:
                # Call Groq API
                response = client.chat.completions.create(
                    model=st.session_state.model,
                    messages=[
                        {"role": "system", "content": "You are an expert meeting assistant that creates concise, structured summaries based on user instructions."},
                        {"role": "user", "content": f"Meeting Transcript:\n{st.session_state.transcript}\n\nInstructions: {st.session_state.custom_prompt}"}
                    ],
                    temperature=0.3,
                    max_tokens=1024,
                    top_p=1
                )
                
                st.session_state.summary = response.choices[0].message.content
                st.session_state.edited_summary = st.session_state.summary
                st.session_state.processing = False
                st.session_state.email_sent = False
                st.success("Summary generated successfully!")
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")
                st.session_state.processing = False

# Output Section
with col2:
    st.markdown('<div class="card"><h2><i class="fas fa-file-contract"></i> Generated Summary</h2></div>', unsafe_allow_html=True)
    
    if st.session_state.processing:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 4rem;">
            <i class="fas fa-spinner fa-spin" style="font-size: 3rem; color: var(--accent);"></i>
            <h3>Processing your meeting notes...</h3>
            <p>This may take a few moments</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Editable summary
        edited_summary = st.text_area("", st.session_state.edited_summary, height=300, 
                                     label_visibility="collapsed", key="summary_editor")
        st.session_state.edited_summary = edited_summary
        
        # Share via email section
        st.markdown('<div class="card"><h2><i class="fas fa-paper-plane"></i> Share via Email</h2></div>', unsafe_allow_html=True)
        
        email_form = st.form(key='email_form')
        with email_form:
            recipients = st.text_input("Recipient Emails (comma separated)", placeholder="email@example.com, another@example.com")
            subject = st.text_input("Email Subject", "Meeting Summary")
            
            if st.form_submit_button("Send Email", type="secondary"):
                if not recipients:
                    st.warning("Please enter at least one recipient email")
                elif not st.session_state.edited_summary.strip():
                    st.warning("Summary is empty")
                else:
                    # Simulate email sending (in a real app, you'd use SMTP or an email service)
                    st.session_state.email_sent = True
                    st.success(f"Email sent to {recipients}!")

# Features section
st.markdown("""
<div class="card">
    <h2 style="text-align: center;"><i class="fas fa-star"></i> Why Choose MeetSumm AI?</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <i class="fas fa-bolt"></i>
            <h3>Lightning Fast</h3>
            <p>Generate summaries in seconds with Groq's ultra-fast inference</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-cogs"></i>
            <h3>Powerful AI</h3>
            <p>Utilizes state-of-the-art LLMs like Mixtral and Llama 3</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-sliders-h"></i>
            <h3>Customizable</h3>
            <p>Tailor summaries with your specific instructions</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-edit"></i>
            <h3>Editable Output</h3>
            <p>Refine AI-generated summaries before sharing</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-share-alt"></i>
            <h3>Easy Sharing</h3>
            <p>Send polished summaries directly to your team</p>
        </div>
        <div class="feature-card">
            <i class="fas fa-lock"></i>
            <h3>Secure</h3>
            <p>Your data remains private and is never stored</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>MeetSumm AI • Powered by Groq & Streamlit • Your AI Meeting Assistant</p>
    <p>Data is processed in real-time and not stored after your session ends</p>
</div>
""", unsafe_allow_html=True)

# JavaScript for model selection
st.markdown("""
<script>
function selectModel(modelId) {
    Streamlit.setComponentValue({model: modelId});
}
</script>
""", unsafe_allow_html=True)

# Handle model selection from JS
model_change = st.session_state.get('model_change', None)
if model_change:
    st.session_state.model = model_change['model']