# Azure AI Document OCR Agent

A production-ready Azure AI Agent for document OCR using Mistral OCR, built with Azure AI Foundry, Microsoft Agent Framework, and Streamlit.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit UI                       │
│              (User Interface)                       │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│            Document OCR Agent                       │
│     (Microsoft Agent Framework)                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│          Mistral OCR Model                          │
│        (Azure AI Foundry)                           │
└─────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│       Azure Infrastructure                          │
│  (Deployed via Pulumi IaC)                          │
│  - AI Hub & Project                                 │
│  - AI Services                                      │
│  - Storage, Key Vault, etc.                         │
└─────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
azure-ocr-agent/
├── agent/
│   ├── __init__.py
│   └── ocr_agent.py          # Core agent logic
├── infra/
│   ├── __main__.py            # Pulumi infrastructure
│   ├── Pulumi.yaml
│   └── requirements.txt
├── app.py                     # Streamlit UI
├── requirements.txt           # Python dependencies
├── .env.template             # Environment variables template
├── .env                      # Your actual config (git ignored)
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Azure subscription
- Azure CLI installed and configured
- Pulumi CLI installed

### Step 1: Clone and Setup

```bash
# Create project directory
mkdir azure-ocr-agent
cd azure-ocr-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Deploy Infrastructure with Pulumi

```bash
# Navigate to infra directory
cd infra

# Login to Pulumi (choose your backend)
pulumi login

# Initialize stack
pulumi stack init dev

# Set Azure configuration
pulumi config set azure-native:location eastus
pulumi config set projectName ocr-agent-demo
pulumi config set tenantId YOUR_AZURE_TENANT_ID

# Deploy infrastructure
pulumi up

# Note the outputs for next steps
pulumi stack output
```

### Step 3: Deploy Mistral OCR Model in Azure AI Foundry

1. Navigate to [Azure AI Foundry](https://ai.azure.com)
2. Open your AI Hub and Project (created by Pulumi)
3. Go to **Model Catalog**
4. Search for **"Mistral OCR"** (mistral-ocr-2503)
5. Click **Deploy** and follow the wizard
6. Copy the **Endpoint URL** and **API Key**

### Step 4: Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit .env and fill in your values
nano .env  # or use your preferred editor
```

Required values in `.env`:
- `MISTRAL_OCR_ENDPOINT`: From AI Foundry deployment
- `MISTRAL_OCR_KEY`: From AI Foundry deployment
- Resource names from `pulumi stack output`

### Step 5: Run the Application

```bash
# Make sure you're in the project root
cd ..

# Run Streamlit app
streamlit run app.py
```

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
