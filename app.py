"""
Streamlit UI for Document OCR Agent
"""
import streamlit as st
from PIL import Image
import io
from datetime import datetime
import sys
import os

# Add agent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

from ocr_agent import create_ocr_agent_from_env, DocumentOCRAgent


# Page configuration
st.set_page_config(
    page_title="Azure AI Document OCR Agent",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078D4;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_agent():
    """Initialize the OCR agent"""
    try:
        if 'agent' not in st.session_state:
            with st.spinner("Initializing Azure AI Agent..."):
                st.session_state.agent = create_ocr_agent_from_env()
                st.session_state.agent_initialized = True
        return st.session_state.agent
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.info("Please ensure your .env file is configured correctly with Azure credentials.")
        return None


def process_uploaded_file(uploaded_file, agent, extract_tables, preserve_formatting):
    """Process the uploaded file with OCR"""
    try:
        # Read image
        image = Image.open(uploaded_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Display the uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📷 Uploaded Document")
            st.image(image, use_container_width=True)
        
        with col2:
            st.subheader("⚙️ Processing...")
            
            # Create progress placeholder
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process document
            status_text.text("Extracting text with Mistral OCR...")
            progress_bar.progress(30)
            
            result = agent.process_document(
                image,
                extract_tables=extract_tables,
                preserve_formatting=preserve_formatting
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Processing complete!")
            
            # Display metrics
            st.markdown("### 📊 Processing Metrics")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Prompt Tokens", result["tokens_used"]["prompt"])
            with metric_col2:
                st.metric("Completion Tokens", result["tokens_used"]["completion"])
            with metric_col3:
                st.metric("Total Tokens", result["tokens_used"]["total"])
        
        return result
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return None


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">📄 Azure AI Document OCR Agent</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subheader">Powered by Mistral OCR on Azure AI Foundry</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Microsoft_Azure_Logo.svg/150px-Microsoft_Azure_Logo.svg.png", width=150)
        st.markdown("## ⚙️ Configuration")
        
        # OCR Options
        st.markdown("### OCR Options")
        extract_tables = st.checkbox("Extract Tables", value=True, help="Format tables in markdown")
        preserve_formatting = st.checkbox("Preserve Formatting", value=True, help="Maintain document structure")
        
        st.markdown("---")
        
        # Agent Info
        st.markdown("### 🤖 Agent Information")
        st.info("""
        **Model:** Mistral OCR 2503
        
        **Capabilities:**
        - High-accuracy text extraction
        - Table detection & formatting
        - Multi-language support
        - Layout preservation
        """)
        
        st.markdown("---")
        
        # About
        st.markdown("### ℹ️ About")
        st.markdown("""
        This demo showcases Azure AI Agent Service with:
        - **Azure AI Foundry** for model deployment
        - **Mistral OCR** for document processing
        - **Microsoft Agent Framework** for orchestration
        - **Pulumi** for infrastructure as code
        """)
    
    # Initialize agent
    agent = initialize_agent()
    
    if agent is None:
        st.warning("⚠️ Agent not initialized. Please check your configuration.")
        return
    
    # Main content area
    st.markdown("## 📤 Upload Document")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a document image (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        help="Upload a scanned document or image containing text"
    )
    
    if uploaded_file is not None:
        # Process the document
        result = process_uploaded_file(uploaded_file, agent, extract_tables, preserve_formatting)
        
        if result:
            st.markdown("---")
            st.markdown("## 📝 Extracted Markdown")
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["📄 Rendered Markdown", "💾 Raw Markdown"])
            
            with tab1:
                # Display rendered markdown
                st.markdown(result["markdown"])
            
            with tab2:
                # Display raw markdown with copy button
                st.code(result["markdown"], language="markdown")
            
            # Download button
            st.markdown("---")
            st.markdown("## 💾 Download Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download as markdown file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ocr_result_{timestamp}.md"
                
                st.download_button(
                    label="📥 Download Markdown",
                    data=result["markdown"],
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col2:
                # Download as text file
                txt_filename = f"ocr_result_{timestamp}.txt"
                
                st.download_button(
                    label="📥 Download Text",
                    data=result["markdown"],
                    file_name=txt_filename,
                    mime="text/plain",
                    use_container_width=True
                )
    
    else:
        # Show example/placeholder
        st.info("👆 Upload a document image to get started")
        
        # Example showcase
        st.markdown("### 📋 Example Use Cases")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📄 Invoices**
            - Extract line items
            - Capture totals
            - Preserve tables
            """)
        
        with col2:
            st.markdown("""
            **📋 Forms**
            - Field extraction
            - Checkbox detection
            - Structure preservation
            """)
        
        with col3:
            st.markdown("""
            **📑 Reports**
            - Full text extraction
            - Header hierarchy
            - Multi-column layouts
            """)


if __name__ == "__main__":
    main()