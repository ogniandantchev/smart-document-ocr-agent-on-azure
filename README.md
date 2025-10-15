# Simple Mistral OCR# Azure AI Document OCR Agent



A clean, minimal implementation for document OCR using Mistral OCR model deployed on a dedicated Azure endpoint.A production-ready Azure AI Agent for document OCR using Mistral OCR, built with Azure AI Foundry, Microsoft Agent Framework, and Streamlit.



## ✨ Features## 🏗️ Architecture



- 📄 **Image Support**: PNG, JPG, JPEG```

- 📑 **PDF Support**: Single and multi-page PDFs┌─────────────────────────────────────────────────────┐

- 🎯 **Simple**: Direct REST API calls, no complex frameworks│                  Streamlit UI                       │

- 🌐 **Web Interface**: Easy-to-use Streamlit app│              (User Interface)                       │

- 💾 **Auto-save**: Extracted text saved as markdown files└─────────────────┬───────────────────────────────────┘

- ⬇️ **Download**: Export as TXT or MD formats                  │

                  ▼

## 🚀 Quick Start┌─────────────────────────────────────────────────────┐

│            Document OCR Agent                       │

### Prerequisites│     (Microsoft Agent Framework)                     │

└─────────────────┬───────────────────────────────────┘

- Python 3.8+                  │

- Mistral OCR model endpoint and API key                  ▼

┌─────────────────────────────────────────────────────┐

### Installation│          Mistral OCR Model                          │

│        (Azure AI Foundry)                           │

1. **Clone and setup**:└─────────────────────────────────────────────────────┘

   ```bash                  │

   git clone <your-repo>                  ▼

   cd simple-mistral-ocr┌─────────────────────────────────────────────────────┐

   pip install -r simple_requirements.txt│       Azure Infrastructure                          │

   ```│  (Deployed via Pulumi IaC)                          │

│  - AI Hub & Project                                 │

2. **Configure environment**:│  - AI Services                                      │

   Create `.env` file:│  - Storage, Key Vault, etc.                         │

   ```bash└─────────────────────────────────────────────────────┘

   MISTRAL_OCR_ENDPOINT=your_mistral_ocr_endpoint```

   MISTRAL_OCR_KEY=your_api_key

   MISTRAL_OCR_MODEL_NAME=mistral-ocr-2503## 📁 Project Structure

   ```

```

3. **Run the web app**:azure-ocr-agent/

   ```bash├── agent/

   streamlit run simple_app.py│   ├── __init__.py

   ```│   └── ocr_agent.py          # Core agent logic

├── infra/

## 📁 Project Structure│   ├── __main__.py            # Pulumi infrastructure

│   ├── Pulumi.yaml

```│   └── requirements.txt

├── simple_ocr.py          # Core OCR implementation├── app.py                     # Streamlit UI

├── simple_app.py          # Streamlit web interface├── requirements.txt           # Python dependencies

├── simple_demo.py         # Test script├── .env.template             # Environment variables template

├── simple_requirements.txt # Dependencies├── .env                      # Your actual config (git ignored)

├── .env                   # Environment variables└── README.md

└── README.md              # This file```

```

## 🚀 Quick Start

## 🔧 Usage

### Prerequisites

### Web Interface

- Python 3.9+

1. **Start the app**: `streamlit run simple_app.py`- Azure subscription

2. **Open browser**: http://localhost:8501- Azure CLI installed and configured

3. **Upload file**: Choose image or PDF- Pulumi CLI installed

4. **Extract text**: Click "Extract Text"

5. **Download**: Get TXT or MD files### Step 1: Clone and Setup



### Command Line```bash

# Create project directory

```pythonmkdir azure-ocr-agent

from simple_ocr import SimpleOCRcd azure-ocr-agent



# Initialize# Create virtual environment

ocr = SimpleOCR()python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

# Extract text from image or PDF

text = ocr.extract_text('path/to/document.pdf')# Install dependencies

print(text)pip install -r requirements.txt

``````



### Demo Script### Step 2: Deploy Infrastructure with Pulumi



```bash```bash

python simple_demo.py# Navigate to infra directory

```cd infra



## 📋 API Reference# Login to Pulumi (choose your backend)

pulumi login

### SimpleOCR Class

# Initialize stack

- `__init__()`: Initialize with environment variablespulumi stack init dev

- `extract_text(file_path)`: Extract markdown text from image/PDF

- `process_file(file_path)`: Get raw API response# Set Azure configuration

- `encode_file(file_path)`: Convert file to base64pulumi config set azure-native:location eastus

pulumi config set projectName ocr-agent-demo

## 🔧 Configurationpulumi config set tenantId YOUR_AZURE_TENANT_ID



Environment variables in `.env`:# Deploy infrastructure

pulumi up

| Variable | Description | Example |

|----------|-------------|---------|# Note the outputs for next steps

| `MISTRAL_OCR_ENDPOINT` | Mistral OCR API endpoint | `https://your-endpoint.com` |pulumi stack output

| `MISTRAL_OCR_KEY` | API authentication key | `your-api-key` |```

| `MISTRAL_OCR_MODEL_NAME` | Model name (optional) | `mistral-ocr-2503` |

### Step 3: Deploy Mistral OCR Model in Azure AI Foundry

## 🎯 What This Gives You

1. Navigate to [Azure AI Foundry](https://ai.azure.com)

- **Clean extracted text** in markdown format2. Open your AI Hub and Project (created by Pulumi)

- **Multi-page PDF support** with page headers3. Go to **Model Catalog**

- **Error handling** and timeout protection4. Search for **"Mistral OCR"** (mistral-ocr-2503)

- **File format detection** (automatic PDF vs image)5. Click **Deploy** and follow the wizard

- **Web interface** for easy testing6. Copy the **Endpoint URL** and **API Key**

- **Auto-save functionality** for extracted content

### Step 4: Configure Environment

## 🛠️ Troubleshooting

```bash

**Connection issues**:# Copy template

- Verify your endpoint URL and API keycp .env.template .env

- Check network connectivity

# Edit .env and fill in your values

**Processing hangs**:nano .env  # or use your preferred editor

- Large files may take time to process```

- 60-second timeout is configured

Required values in `.env`:

**File format errors**:- `MISTRAL_OCR_ENDPOINT`: From AI Foundry deployment

- Supported: PNG, JPG, JPEG, PDF- `MISTRAL_OCR_KEY`: From AI Foundry deployment

- Check file is not corrupted- Resource names from `pulumi stack output`



## 📄 License### Step 5: Run the Application



MIT License - feel free to use and modify!```bash

# Make sure you're in the project root

## 🤝 Contributingcd ..



1. Fork the repository# Run Streamlit app

2. Create a feature branchstreamlit run app.py

3. Make your changes```

4. Submit a pull request
The app will open in your browser at `http://localhost:8501`

## 🎯 Features

### Core Capabilities

- **High-Accuracy OCR**: Powered by Mistral OCR 2503
- **Markdown Output**: Structured, readable format
- **Table Extraction**: Automatic table detection and formatting
- **Layout Preservation**: Maintains document structure
- **Multi-language Support**: Handles multiple languages
- **Token Metrics**: Real-time processing statistics

### User Interface

- **Drag-and-drop Upload**: Simple file upload
- **Live Preview**: See original and processed side-by-side
- **Multiple Views**: Rendered and raw markdown
- **Download Options**: Save as .md or .txt
- **Configuration Panel**: Adjust OCR settings

## 🛠️ Configuration Options

### OCR Settings

```python
agent.process_document(
    image_input,
    system_prompt=None,        # Custom instructions
    extract_tables=True,       # Enable table extraction
    preserve_formatting=True   # Maintain structure
)
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MISTRAL_OCR_ENDPOINT` | Model endpoint URL | Yes |
| `MISTRAL_OCR_KEY` | API authentication key | Yes |
| `MISTRAL_OCR_MODEL_NAME` | Model identifier | No (default: mistral-ocr-2503) |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription | For Pulumi |
| `AZURE_TENANT_ID` | Azure AD tenant ID | For Pulumi |

## 💡 Usage Examples

### Basic Document Processing

```python
from agent.ocr_agent import create_ocr_agent_from_env

# Initialize agent
agent = create_ocr_agent_from_env()

# Process single document
result = agent.process_document("invoice.png")
print(result["markdown"])

# Access metrics
print(f"Tokens used: {result['tokens_used']['total']}")
```

### Multi-page Documents

```python
# Process multiple pages
pages = ["page1.png", "page2.png", "page3.png"]
result = agent.process_multi_page_document(pages)

# Save to file
with open("document.md", "w") as f:
    f.write(result["markdown"])
```

### Custom Processing

```python
# Custom system prompt for specific extraction
custom_prompt = """
Extract only the following information:
- Invoice number
- Date
- Total amount
- Line items with quantities and prices
Format as a structured markdown document.
"""

result = agent.process_document(
    "invoice.png",
    system_prompt=custom_prompt,
    extract_tables=True
)
```

## 🔧 Development

### Adding Custom Features

Extend the `DocumentOCRAgent` class:

```python
# agent/ocr_agent.py

class DocumentOCRAgent:
    def extract_specific_fields(self, image_input, fields: list):
        """Extract specific fields from document"""
        prompt = f"Extract only these fields: {', '.join(fields)}"
        return self.process_document(image_input, system_prompt=prompt)
```

### Testing

```python
# test_agent.py
import pytest
from agent.ocr_agent import DocumentOCRAgent

def test_ocr_processing():
    agent = create_ocr_agent_from_env()
    result = agent.process_document("test_invoice.png")
    
    assert result["markdown"] is not None
    assert result["tokens_used"]["total"] > 0
```

## 📊 Performance & Costs

### Token Usage

- Average invoice: ~500-1000 tokens
- Full page document: ~1000-2000 tokens
- Complex multi-page: ~3000-5000 tokens

### Pricing Estimation

Based on Mistral OCR pricing on Azure:
- Input: ~$0.002 per 1K tokens
- Output: ~$0.006 per 1K tokens
- Average cost per page: ~$0.01-0.02

## 🔒 Security Best Practices

1. **Never commit `.env` files**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use Azure Key Vault** for production:
   ```python
   from azure.keyvault.secrets import SecretClient
   from azure.identity import DefaultAzureCredential
   
   credential = DefaultAzureCredential()
   client = SecretClient(vault_url=vault_url, credential=credential)
   api_key = client.get_secret("mistral-ocr-key").value
   ```

3. **Enable RBAC** on AI resources

4. **Use Managed Identities** where possible

## 🐛 Troubleshooting

### Common Issues

#### "Failed to initialize agent"
- Check `.env` file exists and contains correct values
- Verify Mistral OCR endpoint is accessible
- Ensure API key is valid

#### "Model not found"
- Confirm model is deployed in AI Foundry
- Check model name matches deployment name
- Verify endpoint URL is correct

#### "Pulumi deployment fails"
- Ensure Azure CLI is logged in: `az login`
- Check subscription permissions
- Verify resource names are unique

#### "Streamlit connection error"
- Check firewall settings
- Verify endpoint allows public access
- Test endpoint with curl:
  ```bash
  curl -H "api-key: YOUR_KEY" https://your-endpoint/v1/chat/completions
  ```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Deployment to Production

### Azure App Service

```bash
# Create App Service
az webapp up --name ocr-agent-app --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set \
  --name ocr-agent-app \
  --settings MISTRAL_OCR_ENDPOINT="..." MISTRAL_OCR_KEY="..."
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t ocr-agent .
docker run -p 8501:8501 --env-file .env ocr-agent
```

## 📚 Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Mistral OCR Model Card](https://ai.azure.com/catalog/models/mistral-ocr-2503)
- [Microsoft Agent Framework](https://github.com/microsoft/semantic-kernel)
- [Pulumi Azure Documentation](https://www.pulumi.com/docs/clouds/azure/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Contact your Microsoft partner representative
- Check Azure AI Foundry documentation

## 🎉 Demo Tips for Microsoft Partners

### Preparation Checklist

- [ ] Deploy infrastructure 24 hours before demo
- [ ] Test with sample documents
- [ ] Prepare diverse document types (invoices, forms, reports)
- [ ] Have backup documents ready
- [ ] Test internet connectivity
- [ ] Prepare metrics/cost slides

### Demo Flow

1. **Introduction (2 min)**
   - Show architecture diagram
   - Explain Azure AI Foundry benefits

2. **Live Demo (5 min)**
   - Upload invoice → show real-time processing
   - Display rendered markdown
   - Highlight table extraction
   - Show token metrics
   - Download results

3. **Technical Deep Dive (3 min)**
   - Show agent code structure
   - Explain Pulumi IaC benefits
   - Discuss customization options

4. **Business Value (2 min)**
   - Cost analysis
   - Scalability discussion
   - Integration possibilities

### Key Talking Points

- ✅ **Azure-native**: Fully integrated with Azure ecosystem
- ✅ **Enterprise-ready**: Security, compliance, governance
- ✅ **Scalable**: Pay-as-you-grow model
- ✅ **Customizable**: Extend for specific business needs
- ✅ **Modern stack**: Latest AI capabilities from Microsoft & Mistral

---

**Built for ALSO Microsoft Partners**
