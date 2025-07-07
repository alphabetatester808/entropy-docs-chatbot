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
    page_title="Entropy Documentation AI",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Entropy branding
st.markdown("""
<style>
    .stApp > header {
        background-color: transparent;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .entropy-branding {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: bold;
        font-size: 2.5rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .question-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .question-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    .feature-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        text-align: center;
    }
    .status-success {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
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
        self.cache_duration = timedelta(hours=2)  # Cache for 2 hours
    
    def is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.cache_timestamp:
            return False
        return datetime.now() - self.cache_timestamp < self.cache_duration
    
    def fetch_entropy_docs(self) -> Dict[str, str]:
        """Fetch Entropy documentation files"""
        if self.is_cache_valid() and self.documents_cache:
            return self.documents_cache
        
        base_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        
        try:
            # Get repository tree
            for branch in ['main', 'master']:
                tree_url = f"{base_url}/git/trees/{branch}?recursive=1"
                response = requests.get(tree_url)
                
                if response.status_code == 200:
                    tree_data = response.json()
                    break
            else:
                st.error("❌ Could not access Entropy documentation repository.")
                return {}
            
            # Filter for documentation files
            doc_files = []
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob':
                    file_path = item['path']
                    # Include markdown, text, and other doc formats
                    if any(file_path.endswith(ext) for ext in ['.md', '.txt', '.rst', '.mdx']):
                        # Prioritize important Entropy docs
                        if any(important in file_path.lower() for important in 
                               ['readme', 'getting-started', 'quickstart', 'installation', 'ashlar', 'mining', 'entropy', 'faq']):
                            doc_files.insert(0, file_path)
                        else:
                            doc_files.append(file_path)
            
            documents = {}
            
            if not doc_files:
                st.warning("⚠️ No documentation files found in the Entropy docs repository.")
                return {}
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file_path in enumerate(doc_files):
                status_text.text(f"📄 Loading {file_path}...")
                file_content = self.fetch_file_content(file_path)
                if file_content:
                    documents[file_path] = file_content
                progress_bar.progress((i + 1) / len(doc_files))
                time.sleep(0.1)  # Rate limiting for GitHub API
            
            progress_bar.empty()
            status_text.empty()
            
            # Cache the results
            self.documents_cache = documents
            self.cache_timestamp = datetime.now()
            
            return documents
            
        except Exception as e:
            st.error(f"❌ Error fetching Entropy documentation: {e}")
            return {}
    
    def fetch_file_content(self, file_path: str) -> str:
        """Fetch content of a specific file"""
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content_data = response.json()
                
                # Skip very large files
                size = content_data.get('size', 0)
                if size > 500000:  # 500KB limit
                    return None
                
                if content_data.get('encoding') == 'base64':
                    content = base64.b64decode(content_data['content']).decode('utf-8')
                    return content
                    
        except Exception:
            pass
        
        return None
    
    def prepare_entropy_context(self, documents: Dict[str, str]) -> str:
        """Prepare Entropy-specific context"""
        if not documents:
            return ""
        
        # Organize Entropy docs by importance
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
        
        # Combine in order of importance
        all_files = critical_files + ashlar_files + general_files
        context_parts = []
        current_chars = 0
        max_chars = 150000  # Larger context for Entropy docs
        
        for file_path, content in all_files:
            file_section = f"=== {file_path} ===\n{content}\n\n"
            
            if current_chars + len(file_section) < max_chars:
                context_parts.append(file_section)
                current_chars += len(file_section)
            else:
                break
        
        return "\n".join(context_parts)
    
    def answer_entropy_question(self, question: str) -> str:
        """Answer questions about Entropy using the documentation"""
        
        # Fetch Entropy docs
        if not self.documents_cache or not self.is_cache_valid():
            with st.spinner("🎲 Loading Entropy documentation..."):
                self.documents_cache = self.fetch_entropy_docs()
                
            if not self.documents_cache:
                return "❌ Could not load Entropy documentation. Please try again later."
        
        # Prepare context
        context = self.prepare_entropy_context(self.documents_cache)
        
        if not context:
            return "❌ No Entropy documentation content available."
        
        # Entropy-specific system prompt
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
            with st.spinner("🤔 Analyzing Entropy documentation..."):
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": question}]
                )
            
            return response.content[0].text
            
        except anthropic.AuthenticationError:
            return "❌ Invalid Claude API key. Please check your API key in the sidebar."
        except anthropic.RateLimitError:
            return "❌ Rate limit exceeded. Please wait a moment and try again."
        except Exception as e:
            return f"❌ Error generating response: {str(e)}"

def main():
    # Header with Entropy branding
    st.markdown("""
    <div class="main-header">
        <div class="entropy-branding">🎲 ENTROPY</div>
        <h2>Documentation AI Assistant</h2>
        <p>Get instant answers about mining entropy, Ashlar devices, and the $ENT ecosystem</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔑 API Configuration")
        
        # API Key input
        claude_api_key = st.text_input(
            "Claude API Key", 
            type="password",
            help="Get your API key from https://console.anthropic.com/",
            placeholder="sk-ant-..."
        )
        
        st.markdown("---")
        
        # Quick info about Entropy
        st.markdown("### 🎲 About Entropy")
        st.markdown("""
        **Entropy** is a unique DePIN memecoin where miners generate "useless" randomness using Ashlar devices to earn $ENT tokens.
        
        - 🏗️ **No VCs, no founder allocation**
        - ⛏️ **Fair mining for everyone**
        - 🎯 **Generates literal nothingness**
        - 🌐 **Pure community-driven**
        """)
        
        st.markdown("---")
        
        # Links
        st.markdown("### 🔗 Official Links")
        st.markdown("""
        - 🌐 [Main Site](https://justentropy.lol)
        - 📚 [Documentation](https://github.com/justentropy-lol/entropy-docs)
        - 🛒 [Get Ashlar Device](https://heliumdeploy.com/products/ashlar)
        - 💬 [Discord Community](https://discord.gg/entropy)
        """)
        
        st.markdown("---")
        
        # Instructions
        st.markdown("### 📖 How to Use")
        st.markdown("""
        1. **Enter API Key** above
        2. **Click Initialize** below
        3. **Ask questions** about Entropy!
        
        The AI knows all about:
        - Setting up Ashlar miners
        - $ENT tokenomics
        - Community rules
        - Mining strategies
        - Technical details
        """)
    
    # Main content area
    if not claude_api_key:
        # Welcome screen
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🚀 Welcome to Entropy Documentation AI")
            st.markdown("""
            This AI assistant knows everything about the Entropy project from the official documentation. 
            It can help you with:
            
            - **🔧 Setting up your Ashlar mining device**
            - **💰 Understanding $ENT tokenomics and rewards**
            - **📋 Learning community rules and guidelines**  
            - **🎯 Grasping the philosophy of mining "nothing"**
            - **⚡ Technical troubleshooting and optimization**
            """)
            
            st.info("👈 Enter your Claude API key in the sidebar to get started!")
        
        with col2:
            st.markdown('<div class="feature-box">', unsafe_allow_html=True)
            st.markdown("### 🎲 Pure Entropy")
            st.markdown("Mining nothingness, creating everything.")
            st.markdown("**It's. Just. Entropy. LOL.**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        return
    
    # Initialize chatbot
    if st.button("🎲 Initialize Entropy AI Assistant", type="primary", use_container_width=True):
        try:
            chatbot = EntropyDocsChatbot(claude_api_key)
            st.session_state.entropy_chatbot = chatbot
            st.balloons()
            st.markdown('<div class="status-success">✅ Entropy AI Assistant is ready! Ask me anything about the project.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Failed to initialize: {e}")
    
    # Chat interface
    if 'entropy_chatbot' in st.session_state:
        # Example questions specific to Entropy
        st.markdown("### 💡 Popular Questions")
        
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
        
        # Display questions in a grid
        cols = st.columns(2)
        for i, question in enumerate(entropy_questions):
            with cols[i % 2]:
                if st.button(f"❓ {question}", key=f"q_{i}", use_container_width=True):
                    st.session_state.current_question = question
        
        st.markdown("---")
        
        # Question input
        question = st.text_area(
            "Ask your Entropy question:",
            value=st.session_state.get('current_question', ''),
            height=100,
            placeholder="e.g., How do I start mining entropy with my Ashlar device?"
        )
        
        if st.button("🔍 Get Answer", type="secondary", use_container_width=True) and question:
            answer = st.session_state.entropy_chatbot.answer_entropy_question(question)
            
            st.markdown('<div class="chat-message">', unsafe_allow_html=True)
            st.markdown("### 💬 Answer:")
            st.markdown(answer)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Clear the current question
            if 'current_question' in st.session_state:
                del st.session_state.current_question
        
        # Additional help
        st.markdown("---")
        st.markdown("### 🎯 Need More Help?")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**📚 Documentation**")
            st.markdown("[Read the full docs](https://github.com/justentropy-lol/entropy-docs)")
        
        with col2:
            st.markdown("**💬 Community**")
            st.markdown("[Join Discord](https://discord.gg/entropy)")
        
        with col3:
            st.markdown("**🛒 Get Hardware**")
            st.markdown("[Buy Ashlar Miner](https://heliumdeploy.com/products/ashlar)")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🎲 <strong>ENTROPY</strong> - Culture, Made Mineable</p>
        <p>Built with ❤️ for the Entropy community | Powered by Claude AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
