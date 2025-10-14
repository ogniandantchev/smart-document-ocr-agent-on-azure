"""
Demo script for testing the Document OCR Agent
Run this to verify your setup before the live demo
"""
import sys
import os
from pathlib import Path

# Add agent to path
sys.path.insert(0, str(Path(__file__).parent / "agent"))

from ocr_agent import create_ocr_agent_from_env
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


def test_agent_setup():
    """Test agent initialization"""
    print("=" * 60)
    print("Azure AI Document OCR Agent - Demo Test")
    print("=" * 60)
    print()
    
    try:
        print("1️⃣  Testing agent initialization...")
        agent = create_ocr_agent_from_env()
        print("   ✅ Agent initialized successfully")
        print(f"   Model: {agent.model_name}")
        print(f"   Endpoint: {agent.endpoint[:50]}...")
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
        
        print("3️⃣  Processing document with OCR...")
        result = agent.process_document(str(invoice_path))
        print("   ✅ Document processed successfully")
        print()
        
        print("4️⃣  Results:")
        print("-" * 60)
        print("📊 Metrics:")
        print(f"   Prompt tokens: {result['tokens_used']['prompt']}")
        print(f"   Completion tokens: {result['tokens_used']['completion']}")
        print(f"   Total tokens: {result['tokens_used']['total']}")
        print()
        print("📝 Extracted Markdown (first 500 chars):")
        print("-" * 60)
        print(result['markdown'][:500])
        if len(result['markdown']) > 500:
            print("...")
            print(f"   (Total length: {len(result['markdown'])} characters)")
        print("-" * 60)
        print()
        
        # Save full result
        output_path = test_dir / "sample_invoice_result.md"
        with open(output_path, 'w') as f:
            f.write(result['markdown'])
        print(f"5️⃣  Full result saved to: {output_path}")
        print()
        
        print("=" * 60)
        print("✅ All tests passed! Your setup is ready for the demo.")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review the extracted markdown in test_documents/")
        print("2. Test with your own documents")
        print("3. Run the Streamlit app: streamlit run app.py")
        print()
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure your .env file exists and contains:")
        print("  - MISTRAL_OCR_ENDPOINT")
        print("  - MISTRAL_OCR_KEY")
        print("  - MISTRAL_OCR_MODEL_NAME")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Verify Mistral OCR model is deployed in Azure AI Foundry")
        print("3. Ensure API endpoint is accessible")
        print("4. Check API key is valid")
        return False


if __name__ == "__main__":
    success = test_agent_setup()
    sys.exit(0 if success else 1)