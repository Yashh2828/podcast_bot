import streamlit as st
import requests
import os
from typing import List, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Podcast Gen - AI Script Generator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration - use environment variable or default to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main app styling */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
    }
    
    /* Container styling */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Card styling */
    .css-1y4p8pa {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #e94560, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #eaeaea !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: #a0a0a0 !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #a0a0a0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Step indicator */
    .step-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .step-active {
        background: linear-gradient(135deg, #e94560, #ff6b6b);
        color: white;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
    }
    
    .step-completed {
        background: rgba(76, 175, 80, 0.2);
        color: #4caf50;
        border: 1px solid #4caf50;
    }
    
    .step-pending {
        background: rgba(255, 255, 255, 0.05);
        color: #666;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #e94560, #ff6b6b) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(233, 69, 96, 0.4) !important;
    }
    
    .stButton > button:disabled {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #666 !important;
        box-shadow: none !important;
        cursor: not-allowed;
    }
    
    /* Secondary button */
    .secondary-btn > button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .secondary-btn > button:hover {
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(233, 69, 96, 0.5);
        border-radius: 16px;
        padding: 2rem;
    }
    
    .stFileUploader:hover {
        border-color: #e94560;
        background: rgba(233, 69, 96, 0.05);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #eaeaea !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #e94560 !important;
        box-shadow: 0 0 0 2px rgba(233, 69, 96, 0.2) !important;
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background: #e94560 !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Topic chips */
    .topic-chip {
        display: inline-block;
        background: linear-gradient(135deg, #e94560, #ff6b6b);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Script display */
    .script-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        max-height: 600px;
        overflow-y: auto;
        font-family: 'Georgia', serif;
        line-height: 1.8;
        color: #eaeaea;
        white-space: pre-wrap;
    }
    
    /* Success message */
    .success-message {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid #4caf50;
        border-radius: 12px;
        padding: 1rem;
        color: #4caf50;
        text-align: center;
    }
    
    /* Warning message */
    .warning-message {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid #ffc107;
        border-radius: 12px;
        padding: 1rem;
        color: #ffc107;
        text-align: center;
    }
    
    /* Error message */
    .error-message {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid #f44336;
        border-radius: 12px;
        padding: 1rem;
        color: #f44336;
        text-align: center;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Card grid */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    .info-card-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .info-card-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e94560;
    }
    
    .info-card-label {
        color: #a0a0a0;
        font-size: 0.9rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(233, 69, 96, 0.5), transparent);
        margin: 2rem 0;
    }
    
    /* Label styling */
    label {
        color: #eaeaea !important;
        font-weight: 500 !important;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #eaeaea !important;
        font-family: 'Georgia', serif !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    defaults = {
        'current_step': 1,
        'uploaded_files': [],
        'extracted_topics': [],
        'selected_topics': [],
        'host_name': '',
        'guest_name': '',
        'host_gender': 'male',
        'guest_gender': 'male',
        'host_speed': 100,
        'guest_speed': 100,
        'duration': 15,
        'generated_script': None,
        'script_metadata': {},
        'regenerate_request': '',
        'api_connected': False,
        'warning_message': None,
        'error_message': None,
        'success_message': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# Helper functions
def check_api_connection():
    """Check if backend API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def show_step_indicator():
    """Display step indicator."""
    steps = [
        ("1", "Upload", st.session_state.current_step >= 1),
        ("2", "Topics", st.session_state.current_step >= 2),
        ("3", "Configure", st.session_state.current_step >= 3),
        ("4", "Generate", st.session_state.current_step >= 4),
    ]
    
    html = '<div class="step-container">'
    for i, (num, label, active) in enumerate(steps):
        if i + 1 < st.session_state.current_step:
            css_class = "step-completed"
            icon = "✓"
        elif i + 1 == st.session_state.current_step:
            css_class = "step-active"
            icon = num
        else:
            css_class = "step-pending"
            icon = num
        
        html += f'<div class="step {css_class}"><span>{icon}</span> {label}</div>'
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)


def reset_flow():
    """Reset the entire flow."""
    try:
        requests.post(f"{API_BASE_URL}/api/restart", timeout=10)
    except:
        pass
    
    for key in list(st.session_state.keys()):
        if key not in ['api_connected']:
            del st.session_state[key]
    init_session_state()
    st.rerun()


def extract_topics(files: List) -> Optional[List[str]]:
    """Upload files and extract topics."""
    file_tuples = [("files", (f.name, f.getvalue(), f.type)) for f in files]
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/extract-topics",
            files=file_tuples,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.warning_message = data.get("warning")
            return data.get("topics", [])
        else:
            st.session_state.error_message = f"Error: {response.json().get('detail', 'Unknown error')}"
            return None
    except Exception as e:
        st.session_state.error_message = f"Connection error: {str(e)}"
        return None


def generate_script() -> Optional[str]:
    """Generate podcast script."""
    payload = {
        "host_name": st.session_state.host_name,
        "guest_name": st.session_state.guest_name,
        "host_gender": st.session_state.host_gender,
        "guest_gender": st.session_state.guest_gender,
        "host_speed": st.session_state.host_speed,
        "guest_speed": st.session_state.guest_speed,
        "topics": st.session_state.selected_topics,
        "duration": st.session_state.duration,
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.script_metadata = data.get("metadata", {})
            return data.get("script")
        else:
            st.session_state.error_message = f"Error: {response.json().get('detail', 'Unknown error')}"
            return None
    except Exception as e:
        st.session_state.error_message = f"Connection error: {str(e)}"
        return None


def regenerate_script() -> Optional[str]:
    """Regenerate podcast script with modifications."""
    payload = {
        "host_name": st.session_state.host_name,
        "guest_name": st.session_state.guest_name,
        "host_gender": st.session_state.host_gender,
        "guest_gender": st.session_state.guest_gender,
        "host_speed": st.session_state.host_speed,
        "guest_speed": st.session_state.guest_speed,
        "topics": st.session_state.selected_topics,
        "duration": st.session_state.duration,
        "modification_request": st.session_state.regenerate_request,
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/regenerate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.script_metadata = data.get("metadata", {})
            return data.get("script")
        else:
            st.session_state.error_message = f"Error: {response.json().get('detail', 'Unknown error')}"
            return None
    except Exception as e:
        st.session_state.error_message = f"Connection error: {str(e)}"
        return None


# Main App
st.markdown("<h1>🎙️ Podcast Gen</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>AI-Powered Podcast Script Generator</p>", unsafe_allow_html=True)

# Check API connection
if not st.session_state.api_connected:
    if check_api_connection():
        st.session_state.api_connected = True
    else:
        st.error("⚠️ Cannot connect to backend API. Please ensure the backend server is running on port 8000.")
        st.stop()

# Show step indicator
show_step_indicator()

# Display messages
if st.session_state.error_message:
    st.markdown(f'<div class="error-message">{st.session_state.error_message}</div>', unsafe_allow_html=True)
    st.session_state.error_message = None

if st.session_state.warning_message:
    st.markdown(f'<div class="warning-message">⚠️ {st.session_state.warning_message}</div>', unsafe_allow_html=True)
    st.session_state.warning_message = None

if st.session_state.success_message:
    st.markdown(f'<div class="success-message">✓ {st.session_state.success_message}</div>', unsafe_allow_html=True)
    st.session_state.success_message = None

st.markdown("<hr>", unsafe_allow_html=True)

# STEP 1: File Upload
if st.session_state.current_step == 1:
    st.markdown("<h2>📄 Upload Your Documents</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a0a0a0;'>Upload PDF, DOCX, or TXT files to extract podcast topics.</p>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drop your files here",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.markdown("<h3>Selected Files:</h3>", unsafe_allow_html=True)
        for file in uploaded_files:
            st.markdown(f"<span class='topic-chip'>📄 {file.name}</span>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Extract Topics", use_container_width=True):
                with st.spinner("🔍 Analyzing documents and extracting topics..."):
                    topics = extract_topics(uploaded_files)
                    if topics:
                        st.session_state.extracted_topics = topics
                        st.session_state.uploaded_files = [f.name for f in uploaded_files]
                        st.session_state.current_step = 2
                        st.session_state.success_message = f"Successfully extracted {len(topics)} topics!"
                        st.rerun()

# STEP 2: Topic Selection
elif st.session_state.current_step == 2:
    st.markdown("<h2>🎯 Select Your Topics</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a0a0a0;'>Choose the topics you want to discuss in your podcast.</p>", unsafe_allow_html=True)
    
    # Show extracted topics
    st.markdown("<h3>Extracted Topics:</h3>", unsafe_allow_html=True)
    for topic in st.session_state.extracted_topics:
        st.markdown(f"<span class='topic-chip'>🏷️ {topic}</span>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Multi-select for topics
    selected = st.multiselect(
        "Select topics for your podcast",
        options=st.session_state.extracted_topics,
        default=st.session_state.selected_topics or st.session_state.extracted_topics[:5],
        help="Choose one or more topics to include in your podcast script"
    )
    
    st.session_state.selected_topics = selected
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✓ Confirm Topics", use_container_width=True, disabled=len(selected) == 0):
            if len(selected) > 0:
                st.session_state.current_step = 3
                st.rerun()
            else:
                st.session_state.error_message = "Please select at least one topic."
                st.rerun()

# STEP 3: Configuration
elif st.session_state.current_step == 3:
    st.markdown("<h2>⚙️ Configure Your Podcast</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a0a0a0;'>Set up your host, guest, and podcast preferences.</p>", unsafe_allow_html=True)
    
    # Host Configuration
    st.markdown("<h3>🎤 Host Configuration</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.host_name = st.text_input(
            "Host Name",
            value=st.session_state.host_name,
            placeholder="e.g., Sarah"
        )
    
    with col2:
        st.session_state.host_gender = st.selectbox(
            "Host Gender",
            options=["male", "female", "other"],
            index=["male", "female", "other"].index(st.session_state.host_gender)
        )
    
    with col3:
        st.session_state.host_speed = st.slider(
            "Speaking Speed",
            min_value=50,
            max_value=150,
            value=st.session_state.host_speed,
            help="50 = Slow, 100 = Normal, 150 = Fast"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Guest Configuration
    st.markdown("<h3>🎧 Guest Configuration</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.guest_name = st.text_input(
            "Guest Name",
            value=st.session_state.guest_name,
            placeholder="e.g., Dr. Johnson"
        )
    
    with col2:
        st.session_state.guest_gender = st.selectbox(
            "Guest Gender",
            options=["male", "female", "other"],
            index=["male", "female", "other"].index(st.session_state.guest_gender),
            key="guest_gender_select"
        )
    
    with col3:
        st.session_state.guest_speed = st.slider(
            "Speaking Speed",
            min_value=50,
            max_value=150,
            value=st.session_state.guest_speed,
            help="50 = Slow, 100 = Normal, 150 = Fast",
            key="guest_speed_slider"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Duration
    st.markdown("<h3>⏱️ Podcast Duration</h3>", unsafe_allow_html=True)
    duration_options = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
    st.session_state.duration = st.select_slider(
        "Select duration (minutes)",
        options=duration_options,
        value=st.session_state.duration
    )
    
    # Estimated word count
    word_count = st.session_state.duration * 150
    st.markdown(f"<p style='color: #a0a0a0; text-align: center;'>📊 Estimated word count: ~{word_count:,} words</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        can_proceed = st.session_state.host_name.strip() and st.session_state.guest_name.strip()
        if st.button("🎬 Generate Script", use_container_width=True, disabled=not can_proceed):
            if can_proceed:
                st.session_state.current_step = 4
                st.rerun()
            else:
                st.session_state.error_message = "Please enter both host and guest names."
                st.rerun()

# STEP 4: Generate & Display
elif st.session_state.current_step == 4:
    # Generate script if not already generated
    if st.session_state.generated_script is None:
        with st.spinner("🎙️ Crafting your podcast script... This may take a moment."):
            script = generate_script()
            if script:
                st.session_state.generated_script = script
                st.session_state.success_message = "Podcast script generated successfully!"
                st.rerun()
            else:
                st.stop()
    
    # Display script
    st.markdown("<h2>🎉 Your Podcast Script</h2>", unsafe_allow_html=True)
    
    # Stats cards
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    
    stats = [
        ("🎤", st.session_state.host_name, "Host"),
        ("🎧", st.session_state.guest_name, "Guest"),
        ("⏱️", f"{st.session_state.duration} min", "Duration"),
        ("📊", f"{st.session_state.duration * 150:,}", "Words"),
        ("🏷️", str(len(st.session_state.selected_topics)), "Topics"),
    ]
    
    for icon, value, label in stats:
        st.markdown(f'''
            <div class="info-card">
                <div class="info-card-icon">{icon}</div>
                <div class="info-card-value">{value}</div>
                <div class="info-card-label">{label}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Topic Validation Info
    metadata = st.session_state.script_metadata
    topics_included = metadata.get("topics_included", [])
    topics_ignored = metadata.get("topics_ignored", [])
    
    if topics_included or topics_ignored:
        st.markdown("<h3>🏷️ Topic Analysis</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        if topics_included:
            with col1:
                st.markdown("<div style='background: rgba(76, 175, 80, 0.1); border: 1px solid #4caf50; border-radius: 12px; padding: 1rem;'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #4caf50; margin-top: 0;'>✓ Topics Included</h4>", unsafe_allow_html=True)
                for topic in topics_included:
                    st.markdown(f"• {topic}", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        if topics_ignored:
            with col2:
                st.markdown("<div style='background: rgba(255, 193, 7, 0.1); border: 1px solid #ffc107; border-radius: 12px; padding: 1rem;'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #ffc107; margin-top: 0;'>⚠️ Topics Ignored</h4>", unsafe_allow_html=True)
                st.markdown("<p style='color: #ccc; font-size: 0.9rem;'>These topics were not found in the uploaded documents:</p>", unsafe_allow_html=True)
                for topic in topics_ignored:
                    st.markdown(f"• {topic}", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        if metadata.get("validation_note"):
            st.markdown(f"<p style='color: #a0a0a0; font-size: 0.85rem;'>📝 {metadata.get('validation_note')}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
    
    # Script display
    st.markdown("<h3>📝 Script</h3>", unsafe_allow_html=True)
    st.markdown(f'<div class="script-container">{st.session_state.generated_script}</div>', unsafe_allow_html=True)
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="💾 Download Script",
            data=st.session_state.generated_script,
            file_name=f"podcast_script_{st.session_state.host_name}_{st.session_state.guest_name}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        with st.expander("🔄 Regenerate with Changes"):
            st.session_state.regenerate_request = st.text_area(
                "What would you like to change?",
                placeholder="e.g., Make it more technical, add humor, focus on topic X...",
                value=st.session_state.regenerate_request
            )
            
            if st.button("Regenerate", use_container_width=True):
                if st.session_state.regenerate_request.strip():
                    with st.spinner("🎙️ Regenerating script..."):
                        new_script = regenerate_script()
                        if new_script:
                            st.session_state.generated_script = new_script
                            st.session_state.success_message = "Script regenerated with your changes!"
                            st.rerun()
    
    with col3:
        if st.button("🔄 Start New Podcast", use_container_width=True):
            reset_flow()

# Sidebar info
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎙️ Podcast Gen</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("""
    ### How it works:
    1. **Upload** your documents (PDF, DOCX, TXT)
    2. **Select** topics from extracted content
    3. **Configure** host, guest, and duration
    4. **Generate** your podcast script
    
    ### Features:
    - 🤖 AI-powered script generation
    - 📚 RAG-based content extraction
    - 🎯 Topic selection & validation
    - ⚡ Adjustable speaking speeds
    - 🔄 Regenerate with modifications
    """)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.button("🔄 Restart Flow", use_container_width=True):
        reset_flow()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.8rem;'>Powered by AI ✨</p>", unsafe_allow_html=True)
