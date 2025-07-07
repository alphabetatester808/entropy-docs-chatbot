import streamlit as st
import requests
import anthropic
import base64
from typing import Dict, List
import time
import hashlib
from datetime import datetime, timedelta
import re

# Page config
st.set_page_config(
    page_title="ENTROPY Documentation AI",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API key from secrets
def get_claude_api_key():
    try:
        return st.secrets["CLAUDE_API_KEY"]
    except KeyError:
        st.error("❌ Claude API key not found in secrets. Please contact the administrator.")
        return None

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp > header { background-color: transparent; }
    .stDeployButton { display: none; }
    #MainMenu { display: none; }
    footer { visibility: hidden; }
    .viewerBadge_container__1QSob { display: none; }
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    .entropy-header {
        background-image: url('https://i.imgur.com/xSrtpTL.jpeg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        padding: 4rem 2rem;
        text-align: center;
        border-bottom: 1px solid #2a2a2a;
        position: relative;
        overflow: hidden;
        min-height: 500px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .entropy-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        z-index: 1;
    }
    
    .entropy-banner-content {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4rem;
        max-width: 1200px;
        margin: 0 auto;
        flex-wrap: wrap;
        width: 100%;
    }
    
    .portrait-section {
        flex: 0 0 auto;
        display: flex;
        justify-content: center;
    }
    
    .portrait-container {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: linear-gradient(45deg, #ff6b9d, #9b59b6);
        padding: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 12px 40px rgba(255, 107, 157, 0.4);
    }
    
    .branding-section {
        flex: 1;
        text-align: center;
        max-width: 600px;
    }
    
    .entropy-tagline {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        color: #ffffff;
        font-weight: 800;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
        margin-bottom: 1.5rem;
        text-align: center;
        line-height: 1.2;
    }
    
    .entropy-description {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        color: rgba(255, 255, 255, 0.95);
        line-height: 1.6;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        text-align: center;
    }
    
    .main-content {
        padding: 3rem 2rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .message {
        margin-bottom: 1.5rem;
        padding: 1.5rem;
        border-radius: 12px;
    }
    
    .user-message {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        margin-left: 2rem;
    }
    
    .user-message-header {
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .assistant-message {
        background: #0a0a0a;
        border: 1px solid #ff6b9d;
        margin-right: 2rem;
    }
    
    .assistant-message-header {
        font-weight: 600;
        color: #ff6b9d;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .message-content {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.7;
        color: #e0e0e0;
    }
    
    .citation-link {
        color: #ff6b9d;
        text-decoration: none;
        font-weight: 500;
        border-bottom: 1px dotted #ff6b9d;
        margin-left: 0.5rem;
    }
    
    .citation-link:hover {
        color: #ff5a8e;
        text-decoration: none;
    }
    
    .questions-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .chat-input-container {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        position: sticky;
        bottom: 2rem;
        z-index: 100;
    }
    
    .input-label {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1rem;
        display: block;
    }
    
    .input-hint {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #888888;
        margin-top: 0.5rem;
        text-align: center;
    }
    
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        line-height: 1.5 !important;
    }
    
    .stTextInput input:focus {
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
    
    .sidebar-section {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #ff6b9d;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .sidebar-link {
        display: block;
        color: #e0e0e0;
        text-decoration: none;
        padding: 0.5rem 0;
        border-bottom: 1px solid #2a2a2a;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        transition: color 0.3s ease;
    }
    
    .sidebar-link:hover {
        color: #ff6b9d;
        text-decoration: none;
    }
    
    .sidebar-link:last-child {
        border-bottom: none;
    }
    
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
    
    @media (max-width: 768px) {
        .main-content { padding: 2rem 1rem; }
        .user-message { margin-left: 0; }
        .assistant-message { margin-right: 0; }
        .entropy-header { 
            padding: 3rem 1rem; 
            min-height: 400px;
        }
        .entropy-banner-content { 
            flex-direction: column; 
            gap: 2rem; 
            text-align: center; 
        }
        .portrait-container { 
            width: 140px; 
            height: 140px; 
        }
        .entropy-tagline {
            font-size: 2rem;
        }
        .entropy-description {
            font-size: 1.1rem;
        }
        .branding-section {
            max-width: 100%;
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
    
    def prepare_conversation_context(self, conversation_history: List[Dict]) -> str:
        if not conversation_history:
            return ""
        
        context_parts = []
        for i, exchange in enumerate(conversation_history[-3:]):
            context_parts.append(f"Previous Question {i+1}: {exchange['question']}")
            context_parts.append(f"Previous Answer {i+1}: {exchange['answer'][:500]}...")
        
        return "\n\n".join(context_parts)
    
    def extract_citations(self, response_text: str) -> str:
        """Add citation links to responses based on file references"""
        # Pattern to match file references like "According to README.md" or "As mentioned in getting-started.md"
        file_pattern = r'((?:According to|As mentioned in|Based on|From|In)\s+)([a-zA-Z0-9_-]+\.(?:md|txt|rst|mdx))'
        
        def add_citation_link(match):
            prefix = match.group(1)
            filename = match.group(2)
            github_url = f"https://github.com/{self.repo_owner}/{self.repo_name}/blob/main/{filename}"
            return f'{prefix}<a href="{github_url}" target="_blank" class="citation-link">{filename} 📖</a>'
        
        return re.sub(file_pattern, add_citation_link, response_text, flags=re.IGNORECASE)
    
    def answer_entropy_question(self, question: str, conversation_history: List[Dict] = None) -> str:
        if not self.documents_cache or not self.is_cache_valid():
            with st.spinner("Loading Entropy documentation..."):
                self.documents_cache = self.fetch_entropy_docs()
                
            if not self.documents_cache:
                return "Could not load Entropy documentation. Please try again later."
        
        context = self.prepare_entropy_context(self.documents_cache)
        conversation_context = self.prepare_conversation_context(conversation_history) if conversation_history else ""
        
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

CONVERSATION CONTEXT:
You are having an ongoing conversation with the user. Here's the recent conversation history:
{conversation_context}

STRICT GUIDELINES:
1. Answer ONLY using information from the Entropy documentation provided below
2. If information isn't in the docs, clearly state "This information is not available in the Entropy documentation"
3. ALWAYS cite specific files when referencing information using phrases like "According to README.md" or "As mentioned in getting-started.md"
4. For follow-up questions, reference previous parts of the conversation when relevant
5. If asked to explain something in simpler terms, break down complex concepts step-by-step
6. If asked for more detail, provide deeper explanations from the documentation
7. Embrace the unique nature of Entropy - it's meant to be "useless" and that's the point!
8. Be helpful with setup instructions, mining guidance, and community rules
9. Use the project's own terminology and maintain its playful tone where appropriate
10. IMPORTANT: Always reference the specific documentation file you're citing from

Available Entropy Documentation:
{context}

Remember: You are specifically here to help with Entropy - the project that mines "nothing" but creates community and value through that very nothingness. Use the conversation history to provide more contextual and helpful follow-up responses. Always cite the specific documentation files you reference."""

        try:
            with st.spinner("Analyzing Entropy documentation..."):
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": question}]
                )
            
            response_text = response.content[0].text
            return self.extract_citations(response_text)
            
        except anthropic.AuthenticationError:
            return "Invalid Claude API key. Please check the API key configuration."
        except anthropic.RateLimitError:
            return "Rate limit exceeded. Please wait a moment and try again."
        except Exception as e:
            return f"Error generating response: {str(e)}"

def create_sidebar():
    """Create sidebar with project links and information"""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">🎲 Entropy Project</div>
            <a href="https://justentropy.lol" target="_blank" class="sidebar-link">🌐 Main Website</a>
            <a href="https://github.com/justentropy-lol/entropy-docs" target="_blank" class="sidebar-link">📚 Documentation</a>
            <a href="https://discord.gg/minerseatfirst" target="_blank" class="sidebar-link">💬 Discord Community</a>
            <a href="https://x.com/JustEntropyLol" target="_blank" class="sidebar-link">🐦 Twitter/X</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">⛏️ Mining & Hardware</div>
            <a href="https://heliumdeploy.com/products/ashlar" target="_blank" class="sidebar-link">🔥 Get Ashlar Device</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">💰 Token & Economics</div>
            <a href="https://www.coingecko.com/en/coins/entropy-2" target="_blank" class="sidebar-link">📈 $ENT Price Chart</a>
            <a href="https://solscan.io/token/ENTxR2RP8NtvhXzMNFCxE1HazzdV9x7SuZqGyAb4jdED" target="_blank" class="sidebar-link">🔍 Token Contract</a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">ℹ️ About This AI</div>
            <p style="color: #888; font-size: 0.8rem; margin: 0; padding: 0.5rem 0;">
                This AI assistant provides answers based on official Entropy documentation. 
                All responses include links to the source documents for verification.
            </p>
            <p style="color: #ff6b9d; font-size: 0.8rem; margin: 0; padding: 0.5rem 0;">
                Powered by Claude AI
            </p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Get API key from secrets
    claude_api_key = get_claude_api_key()
    
    # Create sidebar
    create_sidebar()
    
    # Initialize conversation history
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Header
    st.markdown("""
    <div class="entropy-header">
        <div class="entropy-banner-content">
            <div class="portrait-section">
                <div class="portrait-container">
                    <img src="https://i.imgur.com/PGEpQIF.jpeg" alt="Entropy Logo" 
                         style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">
                </div>
            </div>
            <div class="branding-section">
                <div class="entropy-tagline">Documentation AI Assistant</div>
                <div class="entropy-description">
                    Mining nothingness, creating everything.<br>
                    Get instant answers from official Entropy documentation.
                </div>
            </div>
        </div>
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
        
        # Display conversation history
        if st.session_state.conversation_history:
            for exchange in st.session_state.conversation_history:
                # User message
                st.markdown(f"""
                <div class="message user-message">
                    <div class="user-message-header">You asked:</div>
                    <div class="message-content">{exchange['question']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Assistant message with citations
                st.markdown(f"""
                <div class="message assistant-message">
                    <div class="assistant-message-header">🎲 Entropy Response:</div>
                    <div class="message-content">{exchange['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Clear conversation button
            if st.button("🗑️ Clear Conversation", key="clear_conv"):
                st.session_state.conversation_history = []
                st.rerun()
        
        else:
            # Popular questions section (only show when no conversation)
            st.markdown("""
            <div class="questions-title">Popular Questions</div>
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
        
        # Text input with Enter key submission
        question = st.text_input(
            "",
            value=st.session_state.get('current_question', ''),
            placeholder="e.g., How do I start mining entropy with my Ashlar device?",
            key="question_input",
            label_visibility="collapsed"
        )
        
        st.markdown('<div class="input-hint">💡 Press Enter to submit your question, or ask follow-up questions for more details</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle question submission (both button and Enter key)
        if question and (question != st.session_state.get('last_question', '')):
            # Update last question to prevent re-submission
            st.session_state.last_question = question
            
            # Get answer with conversation context
            answer = st.session_state.entropy_chatbot.answer_entropy_question(
                question, 
                st.session_state.conversation_history
            )
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                'question': question,
                'answer': answer,
                'timestamp': datetime.now()
            })
            
            # Clear current question and rerun to show updated conversation
            if 'current_question' in st.session_state:
                del st.session_state.current_question
            
            st.rerun()
    
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
