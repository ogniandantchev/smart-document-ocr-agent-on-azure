"""
Demo script for testing the Document OCR Agent with Microsoft Agent Framework
Run this to verify your setup before the live demo
"""
import asyncio
import sys
import os
from pathlib import Path

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))

from ocr_agent import create_ocr_agent_from_env, setup_observability
from PIL import Image, ImageDraw, ImageFont


def create_sample_invoice():
    """Create a sample invoice image for testing"""
    # Create a simple invoice image
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
        font_bold = ImageFont.load_default()
    
    # Draw invoice content
    y = 50
    draw.text((50, y), "INVOICE", fill='black', font=font_bold)
    y += 60
    
    draw.text((50, y), "Invoice #: INV-2024-001", fill='black', font=font)
    y += 30
    draw.text((50, y), "Date: October 14, 2025", fill='black', font=font)
    y += 30
    draw.text((50, y), "Due Date: November 14, 2025", fill='black', font=font)
    y += 60
    
    draw.text((50, y), "Bill To:", fill='black', font=font_bold)
    y += 30
    draw.text((50, y), "Microsoft Corporation", fill='black', font=font)
    y += 25
    draw.text((50, y), "One Microsoft Way", fill='black', font=font)
    y += 25
    draw.text((50, y), "Redmond, WA 98052", fill='black', font=font)
    y += 60
    
    # Table header
    draw.text((50, y), "Description", fill='black', font=font_bold)
    draw.text((400, y), "Quantity", fill='black', font=font_bold)
    draw.text((550, y), "Price", fill='black', font=font_bold)
    draw.text((700, y), "Total", fill='black', font=font_bold)
    y += 35
    draw.line([(50, y), (750, y)], fill='black', width=2)
    y += 15
    
    # Line items
    items = [
        ("Azure AI Services - OCR", "1000", "$0.02", "$20.00"),
        ("Azure Storage", "500 GB", "$0.02", "$10.00"),
        ("Azure Compute", "100 hrs", "$0.50", "$50.00"),
    ]
    
    for desc, qty, price, total in items:
        draw.text((50, y), desc, fill='black', font=font)
        draw.text((400, y), qty, fill='black', font=font)
        draw.text((550, y), price, fill='black', font=font)
        draw.text((700, y), total, fill='black', font=font)
        y += 30
    
    y += 20
    draw.line([(50, y), (750, y)], fill='black', width=2)
    y += 20
    
    # Total
    draw.text((550, y), "TOTAL:", fill='black', font=font_bold)
    draw.text((700, y), "$80.00", fill='black', font=font_bold)
    
    return img


async def test_agent_setup():
    """Test agent initialization and functionality"""
    print("=" * 70)
    print("Azure AI Document OCR Agent - Demo Test (Agent Framework)")
    print("=" * 70)
    print()
    
    try:
        print("🔧 Setting up OpenTelemetry observability...")
        setup_observability()
        print("   ✅ Observability configured")
        print("   📊 Traces will be sent to AI Toolkit (http://localhost:4317)")
        print()
        
        print("1️⃣  Testing agent initialization...")
        agent = await create_ocr_agent_from_env()
        print("   ✅ Agent Framework agent initialized successfully")
        print(f"   🧠 Using Mistral OCR: {agent.mistral_model_name}")
        print(f"   🔗 Endpoint: {agent.mistral_endpoint[:50]}...")
        print()
        
        # Create test documents directory
        test_dir = Path("test_documents")
        test_dir.mkdir(exist_ok=True)
        
        print("2️⃣  Creating sample invoice...")
        sample_invoice = create_sample_invoice()
        invoice_path = test_dir / "sample_invoice.png"
        sample_invoice.save(invoice_path)
        print(f"   ✅ Sample invoice saved to: {invoice_path}")
        print()
        
        print("3️⃣  Testing agent chat functionality...")
        chat_response = await agent.chat("Hello! Can you explain what you can help me with?")
        print(f"   ✅ Agent response: {chat_response[:100]}...")
        print()
        
        print("4️⃣  Processing document with OCR tool...")
        ocr_message = f"Please extract all text from this invoice image and format it as markdown: {invoice_path}"
        result = await agent.process_document(ocr_message, str(invoice_path))
        print("   ✅ Document processed successfully with Agent Framework")
        print()
        
        print("5️⃣  Testing direct OCR tool functionality...")
        # Test the underlying OCR tool directly
        direct_result = await agent.ocr_tool.extract_text_from_image(
            str(invoice_path),
            extract_tables=True,
            preserve_formatting=True
        )
        print("   ✅ Direct OCR tool test successful")
        print()
        
        print("6️⃣  Results:")
        print("-" * 70)
        print("🤖 Agent Framework Response:")
        print(f"   Length: {len(result)} characters")
        print("   Preview:")
        print(f"   {result[:200]}...")
        print()
        print("📝 Direct OCR Result (first 500 chars):")
        print("-" * 70)
        print(direct_result[:500])
        if len(direct_result) > 500:
            print("...")
            print(f"   (Total length: {len(direct_result)} characters)")
        print("-" * 70)
        print()
        
        # Save results
        agent_output_path = test_dir / "sample_invoice_agent_result.md"
        with open(agent_output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Agent Framework Result\n\n{result}\n\n")
        
        direct_output_path = test_dir / "sample_invoice_direct_result.md"
        with open(direct_output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Direct OCR Tool Result\n\n{direct_result}\n\n")
        
        print(f"7️⃣  Results saved:")
        print(f"   📄 Agent result: {agent_output_path}")
        print(f"   📄 Direct OCR result: {direct_output_path}")
        print()
        
        print("8️⃣  Testing multi-turn conversation...")
        follow_up = await agent.chat("Can you summarize the key information from that invoice?")
        print(f"   ✅ Follow-up response: {follow_up[:100]}...")
        print()
        
        print("=" * 70)
        print("✅ All tests passed! Your Agent Framework setup is ready for the demo.")
        print("=" * 70)
        print()
        print("🎯 Key Features Verified:")
        print("  ✓ Microsoft Agent Framework integration")
        print("  ✓ Mistral OCR tool functionality")
        print("  ✓ OpenTelemetry tracing")
        print("  ✓ Multi-turn conversations")
        print("  ✓ Document processing pipeline")
        print()
        print("🚀 Next steps:")
        print("1. Review the extracted markdown in test_documents/")
        print("2. Open AI Toolkit to view traces: http://localhost:8080")
        print("3. Test with your own documents")
        print("4. Run the Streamlit app: streamlit run app.py")
        print()
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure your .env file exists and contains:")
        print("  - MISTRAL_OCR_ENDPOINT")
        print("  - MISTRAL_OCR_KEY")
        print("  - MISTRAL_OCR_MODEL_NAME (optional)")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print("❌ Traceback:")
        traceback.print_exc()
        print()
        print("🔧 Troubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Verify Mistral OCR model is deployed in Azure AI Foundry")
        print("3. Ensure API endpoint is accessible")
        print("4. Check API key is valid")
        print("5. Verify Agent Framework is installed: pip install agent-framework[azure] --pre")
        print("6. Make sure Azure CLI is authenticated: az login")
        return False


if __name__ == "__main__":
    # Run the async demo
    success = asyncio.run(test_agent_setup())
    sys.exit(0 if success else 1)