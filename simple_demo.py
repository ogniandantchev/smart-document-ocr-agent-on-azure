"""
Simple demo script for Mistral OCR
"""
from simple_ocr import SimpleOCR
from PIL import Image, ImageDraw, ImageFont

def create_test_image():
    """Create a simple test image with text"""
    # Create image
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Add some text
    text_lines = [
        "INVOICE #12345",
        "",
        "Date: October 15, 2025",
        "Customer: Microsoft Corporation",
        "",
        "Description        Qty    Price    Total",
        "Azure AI Services   1     $100     $100",
        "Storage             2     $50      $100",
        "",
        "TOTAL: $200"
    ]
    
    y = 30
    for line in text_lines:
        draw.text((30, y), line, fill='black', font=font)
        y += 35
    
    # Save test image
    img.save("test_invoice.png")
    print("✅ Created test_invoice.png")
    return "test_invoice.png"

def main():
    """Simple demo"""
    print("🚀 Simple Mistral OCR Demo")
    print("-" * 40)
    
    try:
        # Initialize OCR
        ocr = SimpleOCR()
        print("✅ OCR initialized successfully")
        
        # Create test image
        test_image = create_test_image()
        
        # Process image
        print(f"\n📷 Processing {test_image}...")
        result = ocr.extract_text(test_image)
        
        print("\n📝 Extracted Text:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Save result
        with open("simple_result.txt", 'w', encoding='utf-8') as f:
            f.write(result)
        print("\n💾 Result saved to simple_result.txt")
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Check simple_result.txt for the extracted text")
        print("2. Try with your own images")
        print("3. Run the Streamlit app: streamlit run simple_app.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Check your .env file has MISTRAL_OCR_ENDPOINT and MISTRAL_OCR_KEY")
        print("- Verify your Mistral OCR endpoint is correct")
        print("- Make sure the API key is valid")

if __name__ == "__main__":
    main()