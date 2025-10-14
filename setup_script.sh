#!/bin/bash

# Azure AI Document OCR Agent - Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "=========================================="
echo "Azure AI Document OCR Agent - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Check if Azure CLI is installed
echo "📋 Checking Azure CLI..."
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi
echo "✅ Azure CLI detected"
echo ""

# Check if Pulumi is installed
echo "📋 Checking Pulumi..."
if ! command -v pulumi &> /dev/null; then
    echo "❌ Pulumi not found. Please install: https://www.pulumi.com/docs/install/"
    exit 1
fi
echo "✅ Pulumi detected"
echo ""

# Create virtual environment
echo "🔨 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating project structure..."
mkdir -p agent
mkdir -p infra
mkdir -p test_documents
mkdir -p uploads
echo "✅ Directories created"
echo ""

# Copy environment template
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "✅ .env file created"
    echo "⚠️  IMPORTANT: Edit .env file with your Azure credentials!"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Check Azure login
echo "🔐 Checking Azure authentication..."
if az account show &> /dev/null; then
    current_sub=$(az account show --query name -o tsv)
    echo "✅ Logged in to Azure"
    echo "   Subscription: $current_sub"
else
    echo "❌ Not logged in to Azure"
    echo "   Run: az login"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Deploy infrastructure:"
echo "   cd infra && pulumi up"
echo "3. Deploy Mistral OCR model in Azure AI Foundry"
echo "4. Update .env with model endpoint and key"
echo "5. Run the app:"
echo "   streamlit run app.py"
echo ""
echo "For detailed instructions, see README.md"
echo ""