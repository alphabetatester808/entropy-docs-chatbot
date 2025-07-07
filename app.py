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

# Custom CSS with black and pink theme matching the logo
st.markdown("""
<style>
    /* Import clean fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
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
    
    footer {
        visibility: hidden;
    }
    
    .viewerBadge_container__1QSob {
        display: none;
    }
    
    .stAppViewContainer .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Main app styling */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Logo and header */
    .entropy-header {
        background: #000000;
        padding: 2rem 0;
        text-align: center;
        border-bottom: 1px solid #2a2a2a;
    }
    
    .entropy-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #ff6b9d, #c44569);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 1.2rem;
        color: #ffffff;
    }
    
    .logo-text {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.05em;
    }
    
    .entropy-tagline {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #888888;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Main content area */
    .main-content {
        padding: 3rem 2rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Question grid */
    .questions-section {
        margin-bottom: 3rem;
    }
    
    .questions-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .questions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Chat input area */
    .chat-input-container {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    .input-label {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1rem;
        display: block;
    }
    
    /* Chat response area */
    .response-container {
        background: #0a0a0a;
        border: 1px solid #ff6b9d;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 2rem;
    }
    
    .response-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #ff6b9d;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .response-content {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.7;
        color: #e0e0e0;
    }
    
    .response-content h1, .response-content h2, .response-content h3 {
        color: #ffffff;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .response-content h1 {
        font-size: 1.4rem;
        color: #ff6b9d;
    }
    
    .response-content h2 {
        font-size: 1.2rem;
    }
    
    .response-content h3 {
        font-size: 1.1rem;
    }
    
    .response-content code {
        background: #1a1a1a;
        color: #ff6b9d;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }
    
    .response-content pre {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 1rem;
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
        overflow-x: auto;
        margin: 1rem 0;
    }
    
    .response-content ul, .response-content ol {
        padding-left: 1.5rem;
        margin: 1rem 0;
    }
    
    .response-content li {
        margin: 0.5rem 0;
    }
    
    /* Streamlit component overrides */
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        line-height: 1.5 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #ff6b9d !important;
        box-shadow: 0 0 0 1px #ff6b9d !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #ff6b9d, #c44569) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #ff5a8e, #b83e5c) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(255, 107, 157, 0.3) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* Question buttons styling */
    div[data-testid="column"] .stButton button {
        background: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 400 !important;
        padding: 1rem !important;
        font-size: 0.9rem !important;
        text-align: left !important;
        width: 100% !important;
        height: auto !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }
    
    div[data-testid="column"] .stButton button:hover {
        background: #2a2a2a !important;
        border-color: #ff6b9d !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 107, 157, 0.2) !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #1a2e1a !important;
        color: #90ee90 !important;
        border: 1px solid #2d5a2d !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background-color: #2e1a1a !important;
        color: #ff6b6b !important;
        border: 1px solid #5a2d2d !important;
        border-radius: 8px !important;
    }
    
    .stWarning {
        background-color: #2e2a1a !important;
        color: #ffd700 !important;
        border: 1px solid #5a4d2d !important;
        border-radius: 8px !important;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #ff6b9d !important;
    }
    
    /* Footer */
    .entropy-footer {
        background: #000000;
        border-top: 1px solid #2a2a2a;
        padding: 2rem;
        text-align: center;
        margin-top: 4rem;
    }
    
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    
    .footer-link {
        color: #888888;
        text-decoration: none;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        transition: color 0.3s ease;
    }
    
    .footer-link:hover {
        color: #ff6b9d;
    }
    
    .footer-text {
        color: #666666;
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        margin-top: 1rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .questions-grid {
            grid-template-columns: 1fr;
        }
        
        .logo-text {
            font-size: 1.5rem;
        }
        
        .main-content {
            padding: 2rem 1rem;
        }
        
        .chat-input-container, .response-container {
            padding: 1.5rem;
        }
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
    
    # Header with logo
    st.markdown("""
    <div class="entropy-header">
        <div class="entropy-logo">
            <div class="logo-icon">⟐</div>
            <div class="logo-text">ENTROPY</div>
        </div>
        <div class="entropy-tagline">Documentation AI Assistant</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not claude_api_key:
        st.error("Claude API key not configured. Please contact the administrator.")
        return
    
    # Initialize chatbot automatically
    if 'entropy_chatbot' not in st.session_state:
        try:
            st.session_state.entropy_chatbot = EntropyDocsChatbot(claude_api_key)
            st.success("✅ Entropy AI Assistant is ready!")
        except Exception as e:
            st.error(f"Failed to initialize: {e}")
            return
    
    # Main content
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if 'entropy_chatbot' in st.session_state:
        # Popular questions section
        st.markdown("""
        <div class="questions-section">
            <div class="questions-title">Popular Questions</div>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        # Create question grid
        cols = st.columns(2)
        for i, question in enumerate(entropy_questions):
            with cols[i % 2]:
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    st.session_state.current_question = question
        
        # Chat input section
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        st.markdown('<label class="input-label">Ask your question about Entropy:</label>', unsafe_allow_html=True)
        
        question = st.text_area(
            "",
            value=st.session_state.get('current_question', ''),
            height=120,
            placeholder="e.g., How do I start mining entropy with my Ashlar device?",
            key="question_input",
            label_visibility="collapsed"
        )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            ask_button = st.button("Ask Entropy", type="primary", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Response section
        if ask_button and question:
            answer = st.session_state.entropy_chatbot.answer_entropy_question(question)
            
            st.markdown("""
            <div class="response-container">
                <div class="response-title">
                    🎲 Entropy Response
                </div>
                <div class="response-content">
            """, unsafe_allow_html=True)
            
            st.markdown(answer)
            
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Clear the current question
            if 'current_question' in st.session_state:
                del st.session_state.current_question
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="entropy-footer">
        <div class="footer-links">
            <a href="https://justentropy.lol" class="footer-link" target="_blank">Main Site</a>
            <a href="https://github.com/justentropy-lol/entropy-docs" class="footer-link" target="_blank">Documentation</a>
            <a href="https://heliumdeploy.com/products/ashlar" class="footer-link" target="_blank">Get Ashlar Device</a>
            <a href="https://discord.gg/entropy" class="footer-link" target="_blank">Discord Community</a>
        </div>
        <div class="footer-text">
            Built with ❤️ for the Entropy community | Powered by Claude AI
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
