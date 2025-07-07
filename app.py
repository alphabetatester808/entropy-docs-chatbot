import streamlit as st
import requests
import anthropic
import base64
from typing import Dict, List
import time
import hashlib
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="ENTROPY Documentation AI",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Get API key from secrets
def get_claude_api_key():
    try:
        return st.secrets["CLAUDE_API_KEY"]
    except KeyError:
        st.error("❌ Claude API key not found in secrets. Please contact the administrator.")
        return None

# Custom CSS matching justentropy.lol aesthetic
st.markdown("""
<style>
    /* Import similar fonts */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    .stApp > header {
        background-color: transparent;
    }
    
    .stDeployButton {
        display: none;
    }
    
    #MainMenu {
        display: none;
    }
    
    .stAppViewContainer .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
    }
    
    /* Main layout */
    .entropy-container {
        background: #000000;
        color: #ffffff;
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
        padding: 0;
        margin: 0;
    }
    
    /* Header styling - matching justentropy.lol */
    .entropy-header {
        text-align: center;
        padding: 4rem 2rem 2rem 2rem;
        background: #000000;
        border-bottom: 1px solid #333;
    }
    
    .entropy-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.1em;
    }
    
    .entropy-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #888888;
        margin: 1rem 0 0 0;
        font-weight: 400;
    }
    
    .entropy-tagline {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #666666;
        margin: 2rem 0 0 0;
        line-height: 1.6;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Main content area */
    .entropy-main {
        background: #000000;
        padding: 2rem;
        min-height: 60vh;
    }
    
    /* Chat interface */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        background: #111111;
        border: 1px solid #333333;
        border-radius: 0;
        padding: 0;
    }
    
    .chat-input-section {
        padding: 2rem;
        border-bottom: 1px solid #333333;
    }
    
    .chat-response-section {
        padding: 2rem;
        background: #0a0a0a;
        border-top: 1px solid #333333;
    }
    
    /* Typography for responses */
    .entropy-response {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.7;
        color: #e0e0e0;
    }
    
    .entropy-response h1, .entropy-response h2, .entropy-response h3 {
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }
    
    .entropy-response code {
        background: #1a1a1a;
        color: #ffffff;
        padding: 0.2rem 0.4rem;
        border-radius: 2px;
        font-family: 'JetBrains Mono', monospace;
        border: 1px solid #333333;
    }
    
    .entropy-response pre {
        background: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 0;
        padding: 1rem;
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
        overflow-x: auto;
    }
    
    /* Question buttons */
    .question-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .question-btn {
        background: #1a1a1a;
        border: 1px solid #333333;
        color: #ffffff;
        padding: 1rem;
        text-align: left;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border-radius: 0;
    }
    
    .question-btn:hover {
        background: #2a2a2a;
        border-color: #555555;
        transform: translateY(-1px);
    }
    
    /* Footer */
    .entropy-footer {
        background: #000000;
        color: #666666;
        text-align: center;
        padding: 3rem 2rem;
        border-top: 1px solid #333333;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }
    
    /* Streamlit component overrides */
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #555555 !important;
        box-shadow: none !important;
    }
    
    .stButton button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        padding: 0.8rem 2rem !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        background-color: #e0e0e0 !important;
        transform: translateY(-1px) !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1a1a1a !important;
        border-color: #333333 !important;
        border-radius: 0 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Loading spinner */
    .stSpinner {
        color: #ffffff !important;
    }
    
    /* Status messages */
    .stSuccess {
        background-color: #1a2e1a !important;
        color: #90ee90 !important;
        border: 1px solid #2d5a2d !important;
        border-radius: 0 !important;
    }
    
    .stError {
        background-color: #2e1a1a !important;
        color: #ff6b6b !important;
        border: 1px solid #5a2d2d !important;
        border-radius: 0 !important;
    }
    
    /* Hide Streamlit branding */
    footer {
        visibility: hidden;
    }
    
    .viewerBadge_container__1QSob {
        display: none;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 0;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555555;
    }
</style>
""", unsafe_allow_html=True)

class EntropyDocsChatbot:
    def __init__(self, claude_api_key: str):
        self.repo_owner = "justentropy-lol"
        self.repo_name = "entropy-docs"
        self.client = anthropic.Anthropic(api_key=claude_api_key)
        self.documents_cache = {}
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=2)
    
    def is_cache_valid(self) -> bool:
        if not self.cache_timestamp:
            return False
        return datetime.now() - self.cache_timestamp < self.cache_duration
    
    def fetch_entropy_docs(self) -> Dict[str, str]:
        if self.is_cache_valid() and self.documents_cache:
            return self.documents_cache
        
        base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
        try:
            for branch in ['main', 'master']:
                tree_url = f"{base_url}/git/trees/{branch}?recursive=1"
                response = requests.get(tree_url)
                
                if response.status_code == 200:
                    tree_data = response.json()
                    break
            else:
                st.error("Could not access Entropy documentation repository.")
                return {}
            
            doc_files = []
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob':
                    file_path = item['path']
                    if any(file_path.endswith(ext) for ext in ['.md', '.txt', '.rst', '.mdx']):
                        if any(important in file_path.lower() for important in 
                               ['readme', 'getting-started', 'quickstart', 'installation', 'ashlar', 'mining', 'entropy', 'faq']):
                            doc_files.insert(0, file_path)
                        else:
                            doc_files.append(file_path)
            
            documents = {}
            
            if not doc_files:
                st.warning("No documentation files found in the Entropy docs repository.")
                return {}
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file_path in enumerate(doc_files):
                status_text.text(f"Loading {file_path}...")
                file_content = self.fetch_file_content(file_path)
                if file_content:
                    documents[file_path] = file_content
                progress_bar.progress((i + 1) / len(doc_files))
                time.sleep(0.1)
            
            progress_bar.empty()
            status_text.empty()
            
            self.documents_cache = documents
            self.cache_timestamp = datetime.now()
            
            return documents
            
        except Exception as e:
            st.error(f"Error fetching Entropy documentation: {e}")
            return {}
    
    def fetch_file_content(self, file_path: str) -> str:
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content_data = response.json()
                
                size = content_data.get('size', 0)
                if size > 500000:
                    return None
                
                if content_data.get('encoding') == 'base64':
                    content = base64.b64decode(content_data['content']).decode('utf-8')
                    return content
                    
        except Exception:
            pass
        
        return None
    
    def prepare_entropy_context(self, documents: Dict[str, str]) -> str:
        if not documents:
            return ""
        
        critical_files = []
        ashlar_files = []
        general_files = []
        
        for file_path, content in documents.items():
            file_lower = file_path.lower()
            if any(critical in file_lower for critical in ['readme', 'getting-started', 'quickstart']):
                critical_files.append((file_path, content))
            elif any(ashlar in file_lower for ashlar in ['ashlar', 'mining', 'device']):
                ashlar_files.append((file_path, content))
            else:
                general_files.append((file_path, content))
        
        all_files = critical_files + ashlar_files + general_files
        context_parts = []
        current_chars = 0
        max_chars = 150000
        
        for file_path, content in all_files:
            file_section = f"=== {file_path} ===\n{content}\n\n"
            
            if current_chars + len(file_section) < max_chars:
                context_parts.append(file_section)
                current_chars += len(file_section)
            else:
                break
        
        return "\n".join(context_parts)
    
    def answer_entropy_question(self, question: str) -> str:
        if not self.documents_cache or not self.is_cache_valid():
            with st.spinner("Loading Entropy documentation..."):
                self.documents_cache = self.fetch_entropy_docs()
                
            if not self.documents_cache:
                return "Could not load Entropy documentation. Please try again later."
        
        context = self.prepare_entropy_context(self.documents_cache)
        
        if not context:
            return "No Entropy documentation content available."
        
        system_prompt = f"""You are the official Entropy documentation assistant. You help users understand the Entropy project, which is a unique DePIN (Decentralized Physical Infrastructure Network) memecoin that mines "useless" entropy.

Your expertise covers:
- Entropy project overview and philosophy
- Ashlar mining devices and setup
- $ENT token mechanics and mining
- Community rules and guidelines
- Technical aspects of entropy generation
- DePIN concepts as they relate to Entropy

STRICT GUIDELINES:
1. Answer ONLY using information from the Entropy documentation provided below
2. If information isn't in the docs, clearly state "This information is not available in the Entropy documentation"
3. Always cite specific files when referencing information (e.g., "According to README.md...")
4. Embrace the unique nature of Entropy - it's meant to be "useless" and that's the point!
5. Be helpful with setup instructions, mining guidance, and community rules
6. Use the project's own terminology and maintain its playful tone where appropriate
7. Provide step-by-step instructions when available in the docs

Available Entropy Documentation:
{context}

Remember: You are specifically here to help with Entropy - the project that mines "nothing" but creates community and value through that very nothingness. Stay true to the project's unique philosophy while being maximally helpful."""

        try:
            with st.spinner("Analyzing Entropy documentation..."):
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": question}]
                )
            
            return response.content[0].text
            
        except anthropic.AuthenticationError:
            return "Invalid Claude API key. Please check the API key configuration."
        except anthropic.RateLimitError:
            return "Rate limit exceeded. Please wait a moment and try again."
        except Exception as e:
            return f"Error generating response: {str(e)}"

def main():
    # Get API key from secrets
    claude_api_key = get_claude_api_key()
    
    # Create the entropy container
    st.markdown('<div class="entropy-container">', unsafe_allow_html=True)
    
    # Header section - matching justentropy.lol style
    st.markdown("""
    <div class="entropy-header">
        <h1 class="entropy-title">ENTROPY</h1>
        <p class="entropy-subtitle">Documentation AI Assistant</p>
        <p class="entropy-tagline">
            Generate entropy. Earn $ENT.<br>
            You know it.<br><br>
            Ask questions about mining nothing.<br>
            Get answers about everything.<br><br>
            It's. Just. Entropy. LOL.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not claude_api_key:
        st.error("Claude API key not configured. Please contact the administrator.")
        return
    
    # Initialize chatbot automatically
    if 'entropy_chatbot' not in st.session_state:
        try:
            st.session_state.entropy_chatbot = EntropyDocsChatbot(claude_api_key)
            st.success("Entropy AI Assistant is ready.")
        except Exception as e:
            st.error(f"Failed to initialize: {e}")
            return
    
    # Main content area
    st.markdown('<div class="entropy-main">', unsafe_allow_html=True)
    
    if 'entropy_chatbot' in st.session_state:
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Input section
        st.markdown('<div class="chat-input-section">', unsafe_allow_html=True)
        
        # Example questions with custom styling
        entropy_questions = [
            "How do I set up my Ashlar mining device?",
            "What is the Entropy project and how does it work?",
            "How do I earn $ENT tokens through mining?",
            "What are the community rules I need to follow?",
            "How much can I earn mining entropy?",
            "What is the Jeeter Deleter rule?",
            "How do I connect my Ashlar to the network?",
            "What makes Entropy different from other crypto projects?"
        ]
        
        st.markdown("### Popular Questions")
        
        # Create a grid of question buttons
        cols = st.columns(2)
        for i, question in enumerate(entropy_questions):
            with cols[i % 2]:
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    st.session_state.current_question = question
        
        st.markdown("---")
        
        # Question input
        question = st.text_area(
            "Ask your question:",
            value=st.session_state.get('current_question', ''),
            height=120,
            placeholder="e.g., How do I start mining entropy with my Ashlar device?",
            key="question_input"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            ask_button = st.button("ASK ENTROPY", type="primary", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close input section
        
        # Response section
        if ask_button and question:
            st.markdown('<div class="chat-response-section">', unsafe_allow_html=True)
            
            answer = st.session_state.entropy_chatbot.answer_entropy_question(question)
            
            st.markdown('<div class="entropy-response">', unsafe_allow_html=True)
            st.markdown(answer)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Clear the current question
            if 'current_question' in st.session_state:
                del st.session_state.current_question
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close response section
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close chat container
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close main content
    
    # Footer - matching justentropy.lol style
    st.markdown("""
    <div class="entropy-footer">
        <p>© 2025 Just Entropy, Inc. All rights reserved.</p>
        <p>Built with entropy for the entropy community.</p>
        <p>It's. Just. Entropy. LOL.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close entropy container

if __name__ == "__main__":
    main()
