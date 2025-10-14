"""
Streamlit UI for Document OCR Agent with Microsoft Agent Framework
"""
import streamlit as st
from PIL import Image
import io
import asyncio
from datetime import datetime
import sys
import os
import tempfile

# Add agent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

from ocr_agent import create_ocr_agent_from_env, DocumentOCRAgent, setup_observability


# Page configuration
st.set_page_config(
    page_title="Azure AI Document OCR Agent (Agent Framework)",
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
    .agent-framework-badge {
        background: linear-gradient(45deg, #0078D4, #106EBE);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_agent():
    """Initialize the OCR agent (cached)"""
    try:
        # Set up observability
        setup_observability()
        
        # Create agent using async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = loop.run_until_complete(create_ocr_agent_from_env())
        return agent, None
    except Exception as e:
        return None, str(e)


async def process_uploaded_file_async(image_path, agent, extract_tables, preserve_formatting, custom_instructions):
    """Process the uploaded file with OCR using Agent Framework"""
    try:
        # Create the message for the agent
        if custom_instructions:
            message = f"""Please extract text from this document image and format it as markdown.
            
Custom instructions: {custom_instructions}

Settings:
- Extract tables: {extract_tables}
- Preserve formatting: {preserve_formatting}

Image path: {image_path}"""
        else:
            message = f"""Please extract text from this document image and format it as markdown.

Settings:
- Extract tables: {extract_tables}
- Preserve formatting: {preserve_formatting}

Image path: {image_path}"""
        
        # Process with the agent
        result = await agent.process_document(message, image_path)
        
        # Also get direct OCR result for comparison
        direct_result = await agent.ocr_tool.extract_text_from_image(
            image_path,
            extract_tables=extract_tables,
            preserve_formatting=preserve_formatting,
            custom_instructions=custom_instructions
        )
        
        return {
            "agent_response": result,
            "direct_ocr": direct_result,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def process_uploaded_file(uploaded_file, agent, extract_tables, preserve_formatting, custom_instructions):
    """Synchronous wrapper for async processing"""
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            # Read image
            image = Image.open(uploaded_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to temporary file
            image.save(tmp_file.name, format='PNG')
            image_path = tmp_file.name
        
        # Display the uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📷 Uploaded Document")
            st.image(image, use_container_width=True)
        
        with col2:
            st.subheader("⚙️ Processing with Agent Framework...")
            
            # Create progress placeholder
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process document
            status_text.text("🤖 Initializing Agent Framework...")
            progress_bar.progress(20)
            
            status_text.text("🧠 Processing with Mistral OCR tool...")
            progress_bar.progress(50)
            
            # Run async processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                process_uploaded_file_async(
                    image_path, agent, extract_tables, 
                    preserve_formatting, custom_instructions
                )
            )
            
            progress_bar.progress(100)
            
            if result["success"]:
                status_text.text("✅ Processing complete!")
                
                # Display agent info
                st.markdown("### 🤖 Agent Framework Info")
                st.markdown('<div class="agent-framework-badge">Microsoft Agent Framework</div>', unsafe_allow_html=True)
                st.info(f"**Agent:** {agent.__class__.__name__}\n**Model:** {agent.mistral_model_name}")
            else:
                status_text.text("❌ Processing failed!")
                st.error(f"Error: {result['error']}")
                return None
        
        # Cleanup
        try:
            os.unlink(image_path)
        except:
            pass
        
        return result
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return None


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">📄 Azure AI Document OCR Agent</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subheader">Powered by Microsoft Agent Framework + Mistral OCR</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Microsoft_Azure_Logo.svg/150px-Microsoft_Azure_Logo.svg.png", width=150)
        st.markdown("## ⚙️ Configuration")
        
        # OCR Options
        st.markdown("### 📝 OCR Options")
        extract_tables = st.checkbox("Extract Tables", value=True, help="Format tables in markdown")
        preserve_formatting = st.checkbox("Preserve Formatting", value=True, help="Maintain document structure")
        
        # Custom instructions
        custom_instructions = st.text_area(
            "Custom Instructions", 
            placeholder="Optional: Add specific instructions for text extraction...",
            help="Provide additional context or requirements for the OCR process"
        )
        
        st.markdown("---")
        
        # Observability
        st.markdown("### 📊 Observability")
        if st.button("🔍 Open AI Toolkit Tracing"):
            st.markdown("Open [AI Toolkit Tracing](http://localhost:8080) in a new tab")
        
        st.info("OpenTelemetry traces are being sent to AI Toolkit for Visual Studio Code")
        
        st.markdown("---")
        
        # Agent Info
        st.markdown("### 🤖 Agent Information")
        st.info("""
        **Framework:** Microsoft Agent Framework
        
        **OCR Model:** Mistral OCR 2503
        
        **Capabilities:**
        - High-accuracy text extraction
        - Table detection & formatting
        - Multi-language support
        - Layout preservation
        - Conversational interface
        - Tool-based architecture
        """)
        
        st.markdown("---")
        
        # About
        st.markdown("### ℹ️ About")
        st.markdown("""
        This demo showcases:
        - **Microsoft Agent Framework** for AI orchestration
        - **Azure AI Foundry** for model deployment
        - **Mistral OCR** as an agent tool
        - **OpenTelemetry** for observability
        - **Pulumi** for infrastructure as code
        """)
    
    # Initialize agent
    agent, error = initialize_agent()
    
    if agent is None:
        st.error(f"⚠️ Failed to initialize Agent Framework: {error}")
        st.info("""
        Please ensure:
        1. Your .env file contains MISTRAL_OCR_ENDPOINT and MISTRAL_OCR_KEY
        2. Agent Framework is installed: `pip install agent-framework[azure] --pre`
        3. Azure CLI is authenticated: `az login`
        """)
        return
    
    # Success message
    st.success("✅ Agent Framework initialized successfully!")
    
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
        result = process_uploaded_file(
            uploaded_file, agent, extract_tables, 
            preserve_formatting, custom_instructions
        )
        
        if result and result.get("success"):
            st.markdown("---")
            st.markdown("## 📝 Results")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["🤖 Agent Response", "📄 Direct OCR", "💾 Raw Output"])
            
            with tab1:
                st.markdown("### Agent Framework Response")
                st.markdown("*This is the full response from the Agent Framework, which may include additional context and formatting:*")
                st.markdown(result["agent_response"])
            
            with tab2:
                st.markdown("### Direct OCR Tool Output")
                st.markdown("*This is the direct output from the Mistral OCR tool:*")
                st.markdown(result["direct_ocr"])
            
            with tab3:
                st.markdown("### Raw Outputs")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Agent Response (Raw)**")
                    st.code(result["agent_response"], language="markdown")
                
                with col2:
                    st.markdown("**OCR Tool (Raw)**")
                    st.code(result["direct_ocr"], language="markdown")
            
            # Download section
            st.markdown("---")
            st.markdown("## 💾 Download Results")
            
            col1, col2, col3 = st.columns(3)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with col1:
                # Download agent response
                agent_filename = f"agent_response_{timestamp}.md"
                st.download_button(
                    label="📥 Download Agent Response",
                    data=result["agent_response"],
                    file_name=agent_filename,
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col2:
                # Download OCR result
                ocr_filename = f"ocr_result_{timestamp}.md"
                st.download_button(
                    label="📥 Download OCR Result",
                    data=result["direct_ocr"],
                    file_name=ocr_filename,
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col3:
                # Download combined
                combined_content = f"# Agent Framework Response\n\n{result['agent_response']}\n\n---\n\n# Direct OCR Tool Result\n\n{result['direct_ocr']}"
                combined_filename = f"combined_results_{timestamp}.md"
                st.download_button(
                    label="📥 Download Combined",
                    data=combined_content,
                    file_name=combined_filename,
                    mime="text/markdown",
                    use_container_width=True
                )
    
    else:
        # Show example/placeholder
        st.info("👆 Upload a document image to get started with the Agent Framework")
        
        # Example showcase
        st.markdown("### 📋 Agent Framework Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🤖 Intelligent Agent**
            - Conversational interface
            - Context awareness
            - Tool orchestration
            - Multi-turn conversations
            """)
        
        with col2:
            st.markdown("""
            **� OCR Tool Integration**
            - Mistral OCR as agent tool
            - Flexible processing options
            - Custom instructions
            - Error handling
            """)
        
        with col3:
            st.markdown("""
            **� Observability**
            - OpenTelemetry tracing
            - AI Toolkit integration
            - Performance monitoring
            - Debug insights
            """)
        
        # Chat interface
        st.markdown("---")
        st.markdown("## 💬 Chat with the Agent")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat input
        user_message = st.chat_input("Ask the agent about OCR capabilities or document processing...")
        
        if user_message:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            # Get agent response
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                agent_response = loop.run_until_complete(agent.chat(user_message))
                st.session_state.chat_history.append({"role": "assistant", "content": agent_response})
            except Exception as e:
                st.error(f"Error getting agent response: {e}")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])


if __name__ == "__main__":
    main()