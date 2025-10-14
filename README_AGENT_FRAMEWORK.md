# Azure AI Document OCR Agent - Microsoft Agent Framework Edition

## 🎯 Overview

This project has been completely reworked to use the **Microsoft Agent Framework**, implementing a conversational AI agent that uses Mistral OCR as a tool for document processing. The new architecture provides better orchestration, observability, and a more natural interaction model.

## 🏗️ Architecture

### Key Components

1. **Microsoft Agent Framework**
   - `ChatAgent` as the main orchestrator
   - `AzureAIAgentClient` for Azure integration
   - Tool-based architecture for OCR functionality

2. **Mistral OCR Tool**
   - Encapsulated as an agent tool
   - Supports single and multi-page processing
   - Customizable instructions and settings

3. **OpenTelemetry Observability**
   - Integrated tracing for AI Toolkit
   - End-to-end monitoring of agent interactions
   - Performance and debugging insights

4. **Streamlit UI**
   - Enhanced interface with Agent Framework features
   - Chat functionality with the agent
   - Multiple output views (agent vs direct OCR)

## 🚀 Quick Start

### Prerequisites

1. **Azure CLI** authenticated: `az login`
2. **Python 3.9+**
3. **Visual Studio Code** with AI Toolkit extension (for observability)
4. **Mistral OCR model** deployed in Azure AI Foundry

### Installation

1. **Clone and setup environment:**
   ```bash
   git clone <your-repo>
   cd a3
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your Mistral OCR credentials
   ```

4. **Start AI Toolkit for tracing (optional):**
   - Open Visual Studio Code
   - Install AI Toolkit extension
   - The tracing endpoint will be available at `http://localhost:4317`

### Running the Application

1. **Test the setup:**
   ```bash
   python demo.py
   ```

2. **Launch the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

3. **View traces:**
   - Open AI Toolkit in VS Code
   - Navigate to the tracing section
   - Monitor agent interactions and performance

## 🔧 Configuration

### Environment Variables

```env
# Mistral OCR Configuration
MISTRAL_OCR_ENDPOINT=https://your-mistral-endpoint.inference.ai.azure.com
MISTRAL_OCR_KEY=your-api-key-here
MISTRAL_OCR_MODEL_NAME=mistral-ocr-2503

# OpenTelemetry (for AI Toolkit)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### Agent Configuration

The agent can be customized with different instructions and tools:

```python
agent = DocumentOCRAgent(
    mistral_endpoint="your-endpoint",
    mistral_api_key="your-key",
    agent_instructions="Custom instructions for your use case"
)
```

## 🛠️ Usage Examples

### Basic Chat Interaction

```python
import asyncio
from agent.ocr_agent import create_ocr_agent_from_env

async def main():
    agent = await create_ocr_agent_from_env()
    
    # Chat with the agent
    response = await agent.chat("What can you help me with?")
    print(response)
    
    # Process a document
    result = await agent.process_document(
        "Please extract text from this invoice", 
        image_path="/path/to/invoice.jpg"
    )
    print(result)

asyncio.run(main())
```

### Direct OCR Tool Usage

```python
# Access the underlying OCR tool directly
ocr_result = await agent.ocr_tool.extract_text_from_image(
    image_path="/path/to/document.png",
    extract_tables=True,
    preserve_formatting=True,
    custom_instructions="Focus on extracting financial data"
)
```

### Multi-Page Processing

```python
# Process multiple pages
pages = ["/path/to/page1.jpg", "/path/to/page2.jpg"]
combined_result = await agent.ocr_tool.extract_text_from_multiple_images(
    image_paths=pages,
    custom_instructions="This is a multi-page contract"
)
```

## 📊 Observability

### OpenTelemetry Integration

The application includes built-in OpenTelemetry tracing:

```python
from agent.ocr_agent import setup_observability

# Enable tracing
setup_observability(enable_sensitive_data=True)
```

### Available Traces

- Agent conversation flows
- OCR tool invocations
- API calls to Mistral OCR
- Performance metrics
- Error tracking

### Viewing Traces

1. Open Visual Studio Code
2. Install the AI Toolkit extension
3. Navigate to the tracing section
4. View real-time traces and metrics

## 🎨 UI Features

### Streamlit Application

The updated Streamlit app includes:

1. **Agent Framework Integration**
   - Real-time chat with the OCR agent
   - Multi-turn conversations
   - Context-aware responses

2. **Enhanced Processing**
   - Agent responses vs direct OCR comparison
   - Custom instruction support
   - Progress tracking with Agent Framework steps

3. **Observability Links**
   - Direct links to AI Toolkit tracing
   - Performance monitoring
   - Debug information

4. **Download Options**
   - Agent responses
   - Direct OCR results
   - Combined outputs

## 🔄 Migration from Previous Version

### Key Changes

1. **Architecture:**
   - `DocumentOCRAgent` now uses Agent Framework
   - OCR functionality moved to tools
   - Async/await pattern throughout

2. **API Changes:**
   - `process_document()` now returns agent response (string)
   - Direct OCR available via `agent.ocr_tool`
   - All operations are now async

3. **Dependencies:**
   - Added `agent-framework[azure]`
   - Added OpenTelemetry packages
   - Removed `semantic-kernel`

### Migration Steps

1. Update your code to use async/await
2. Replace direct OCR calls with agent interactions
3. Update imports to use new modules
4. Configure OpenTelemetry if desired

## 🧪 Testing

### Demo Script

Run the comprehensive demo:

```bash
python demo.py
```

This will:
- Test Agent Framework initialization
- Create sample documents
- Test OCR processing
- Verify observability setup
- Generate test outputs

### Manual Testing

1. **Chat functionality:**
   - Ask the agent about its capabilities
   - Request document processing
   - Follow up with questions

2. **OCR processing:**
   - Upload various document types
   - Test with different settings
   - Verify markdown output quality

3. **Observability:**
   - Check traces in AI Toolkit
   - Monitor performance metrics
   - Verify error handling

## 🚀 Deployment

### Infrastructure

The infrastructure setup remains the same:

```bash
cd infra
pulumi up
```

### Application Deployment

Deploy the updated application using your preferred method:

1. **Container deployment** (recommended)
2. **Azure App Service**
3. **Azure Container Instances**

Make sure to include the Agent Framework dependencies in your deployment.

## 🔍 Troubleshooting

### Common Issues

1. **Agent Framework Import Errors:**
   ```bash
   pip install agent-framework[azure] --pre
   ```

2. **Azure Authentication:**
   ```bash
   az login
   ```

3. **Mistral OCR Connectivity:**
   - Verify endpoint URL
   - Check API key validity
   - Ensure model is deployed

4. **Observability Issues:**
   - Start AI Toolkit in VS Code
   - Check port 4317 availability
   - Verify OpenTelemetry configuration

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Resources

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry](https://ai.azure.com)
- [AI Toolkit for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-windows-ai-studio.windows-ai-studio)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the demo script
5. Submit a pull request

## 📄 License

MIT License

---

## ⚡ What's New in Agent Framework Edition

### ✨ Enhanced Features

- **Conversational Interface:** Natural language interactions with the OCR agent
- **Tool Integration:** Mistral OCR is now a proper agent tool
- **Observability:** Built-in OpenTelemetry tracing
- **Multi-turn Conversations:** Context-aware follow-up questions
- **Improved Error Handling:** Better error messages and recovery
- **Enhanced UI:** Richer Streamlit interface with chat functionality

### 🏃‍♂️ Performance Improvements

- **Async Architecture:** Better performance and responsiveness
- **Optimized Processing:** Streamlined OCR pipeline
- **Memory Management:** Better resource utilization
- **Monitoring:** Real-time performance tracking

### 🔒 Security Enhancements

- **Azure Identity Integration:** Secure authentication
- **Token Management:** Automatic credential handling
- **Audit Trails:** Complete tracing of operations
- **Error Sanitization:** Secure error handling

---

Ready to experience the power of Microsoft Agent Framework with intelligent document OCR? Get started today! 🚀