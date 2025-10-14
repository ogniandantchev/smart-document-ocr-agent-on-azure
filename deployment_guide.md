# Deployment Guide - Azure AI Document OCR Agent

This guide provides step-by-step instructions for deploying the OCR agent for Microsoft partner demos.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Azure subscription with appropriate permissions
- [ ] Azure CLI installed (`az --version`)
- [ ] Pulumi CLI installed (`pulumi version`)
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Git installed (optional, for version control)
- [ ] Text editor (VS Code recommended)

## 🚀 Deployment Steps

### Phase 1: Initial Setup (15 minutes)

#### 1.1 Clone or Create Project Directory

```bash
# Create project directory
mkdir azure-ocr-agent-demo
cd azure-ocr-agent-demo

# Create subdirectories
mkdir -p agent infra test_documents uploads
```

#### 1.2 Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate

# Verify activation
which python  # Should show venv path
```

#### 1.3 Install Dependencies

Create and populate all files from the artifacts, then:

```bash
# Install main dependencies
pip install -r requirements.txt

# Install infrastructure dependencies
cd infra
pip install -r requirements.txt
cd ..
```

### Phase 2: Azure Infrastructure (20 minutes)

#### 2.1 Azure Authentication

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account list --output table
az account set --subscription "Your-Subscription-Name"

# Verify
az account show
```

#### 2.2 Configure Pulumi

```bash
cd infra

# Login to Pulumi (choose backend)
# Option 1: Pulumi Cloud (easiest)
pulumi login

# Option 2: Local backend
# pulumi login --local

# Initialize new stack
pulumi stack init dev

# Configure Azure settings
pulumi config set azure-native:location eastus
pulumi config set projectName ocr-demo-$(date +%s)  # Unique name
pulumi config set tenantId $(az account show --query tenantId -o tsv)
```

#### 2.3 Deploy Infrastructure

```bash
# Preview deployment
pulumi preview

# Deploy (confirm with 'yes')
pulumi up

# Save outputs for later
pulumi stack output --json > ../deployment-outputs.json
cd ..
```

**Expected Resources Created:**
- Resource Group
- Storage Account
- Key Vault
- Application Insights
- AI Hub (Machine Learning Workspace)
- AI Project
- AI Services Account

### Phase 3: Model Deployment (10 minutes)

#### 3.1 Access Azure AI Foundry

1. Navigate to https://ai.azure.com
2. Sign in with your Azure credentials
3. Select your subscription
4. Find your AI Hub (name from Pulumi output)
5. Navigate to your AI Project

#### 3.2 Deploy Mistral OCR Model

1. In AI Foundry, click **Model catalog**
2. Search for "Mistral OCR" or use direct link:
   ```
   https://ai.azure.com/catalog/models/mistral-ocr-2503
   ```
3. Click **Deploy**
4. Configure deployment:
   - Deployment name: `mistral-ocr-deployment`
   - Deployment type: `Serverless API`
   - Virtual machine: (auto-selected)
5. Click **Deploy** and wait (5-10 minutes)

#### 3.3 Get Model Credentials

After deployment:

1. Go to **Deployments** in AI Foundry
2. Click on `mistral-ocr-deployment`
3. Copy the following:
   - **Endpoint URL** (looks like: https://xxx.inference.ai.azure.com/...)
   - **API Key** (under Keys and Endpoints)

### Phase 4: Application Configuration (5 minutes)

#### 4.1 Configure Environment Variables

```bash
# Copy template
cp .env.template .env

# Edit .env file
nano .env  # or use your preferred editor
```

Fill in these critical values:

```bash
# From Pulumi outputs
AZURE_SUBSCRIPTION_ID=xxx-xxx-xxx
AZURE_TENANT_ID=xxx-xxx-xxx
AZURE_AI_PROJECT_NAME=ocr-demo-xxxxx-project
AZURE_AI_RESOURCE_GROUP=ocr-demo-xxxxx-rg
AZURE_AI_HUB_NAME=ocr-demo-xxxxx-hub

# From AI Foundry deployment
MISTRAL_OCR_ENDPOINT=https://your-endpoint.inference.ai.azure.com
MISTRAL_OCR_KEY=your-very-long-api-key
MISTRAL_OCR_MODEL_NAME=mistral-ocr-2503

# Agent config (optional)
AGENT_NAME=DocumentOCRAgent
AGENT_DESCRIPTION=AI Agent for document OCR
```

#### 4.2 Verify Configuration

```bash
# Test the setup
python demo.py
```

Expected output:
```
✅ Agent initialized successfully
✅ Sample invoice saved
✅ Document processed successfully
```

### Phase 5: Launch Application (2 minutes)

```bash
# Run Streamlit app
streamlit run app.py
```

The app should open automatically at http://localhost:8501

## ✅ Verification Checklist

Test each feature:

- [ ] App loads without errors
- [ ] Can upload an image file
- [ ] OCR processing completes
- [ ] Markdown is displayed correctly
- [ ] Tables are formatted properly
- [ ] Can download results
- [ ] Metrics are shown
- [ ] No error messages in console

## 🎯 Pre-Demo Preparation

### Day Before Demo

1. **Deploy fresh infrastructure**
   ```bash
   cd infra
   pulumi up
   ```

2. **Test with actual documents**
   - Upload 3-5 different document types
   - Verify accuracy of extraction
   - Note processing times

3. **Prepare backup scenarios**
   - Save processed results as screenshots
   - Have backup documents ready
   - Test internet connectivity

4. **Document costs**
   ```bash
   # Check token usage from demo.py
   # Calculate: tokens * price per token
   ```

### Morning of Demo

1. **Start fresh session**
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

2. **Verify endpoint connectivity**
   ```bash
   curl -X POST $MISTRAL_OCR_ENDPOINT/v1/chat/completions \
     -H "api-key: $MISTRAL_OCR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"test"}],"model":"mistral-ocr-2503","max_tokens":10}'
   ```

3. **Load test documents**
   - Place in `test_documents/` folder
   - Have variety: invoices, forms, reports

## 🐛 Troubleshooting

### Issue: "Module not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Authentication failed"

```bash
# Re-login to Azure
az login
az account set --subscription "Your-Subscription"
```

### Issue: "Endpoint not accessible"

1. Check firewall settings in Azure Portal
2. Verify public access is enabled
3. Check API key hasn't expired

### Issue: "Model not found"

```bash
# Verify deployment in AI Foundry
# Check model name matches exactly
echo $MISTRAL_OCR_MODEL_NAME
```

### Issue: "Pulumi state locked"

```bash
cd infra
pulumi cancel  # Cancel any pending operations
pulumi refresh  # Sync state
```

## 🔄 Updating the Deployment

### Update Application Code

```bash
# Pull latest changes (if using git)
git pull

# Restart Streamlit
# Press Ctrl+C, then:
streamlit run app.py
```

### Update Infrastructure

```bash
cd infra
pulumi up
cd ..
```

### Redeploy Model

1. Delete old deployment in AI Foundry
2. Deploy new version
3. Update .env with new endpoint/key

## 🧹 Cleanup After Demo

### Remove Application

```bash
# Stop Streamlit (Ctrl+C)
deactivate  # Exit virtual environment
```

### Remove Azure Resources

```bash
cd infra

# Destroy all resources
pulumi destroy  # Type 'yes' to confirm

# Remove stack
pulumi stack rm dev

cd ..
```

### Cost Verification

```bash
# Check Azure costs
az consumption usage list \
  --start-date $(date -d "7 days ago" +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  --query "[].{Service:meterCategory, Cost:pretaxCost}" \
  --output table
```

## 📊 Demo Metrics to Track

During your demo, capture:

1. **Performance Metrics**
   - Processing time per document
   - Tokens used per document
   - Accuracy of extraction

2. **Cost Metrics**
   - Cost per document
   - Total tokens consumed
   - Infrastructure costs

3. **Quality Metrics**
   - Table extraction accuracy
   - Formatting preservation
   - Multi-language handling

## 🎓 Demo Best Practices

1. **Start with simple document** (clean invoice)
2. **Progress to complex** (multi