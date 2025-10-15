"""
Simple Mistral OCR implementation for dedicated Azure endpoint
Uses Mistral OCR model deployed on a dedicated Azure endpoint
"""
import os
import base64
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleOCR:
    """Simple OCR using Mistral OCR model on dedicated Azure endpoint"""
    
    def __init__(self):
        """Initialize with environment variables"""
        self.endpoint = os.getenv("MISTRAL_OCR_ENDPOINT")
        self.api_key = os.getenv("MISTRAL_OCR_KEY")
        self.model_name = os.getenv("MISTRAL_OCR_MODEL_NAME", "mistral-ocr-2503")
        
        if not self.endpoint or not self.api_key:
            raise ValueError("Missing MISTRAL_OCR_ENDPOINT or MISTRAL_OCR_KEY in environment variables")
    
    def encode_file(self, file_path):
        """Encode image or PDF file to base64"""
        file_ext = Path(file_path).suffix.lower()
        
        with open(file_path, "rb") as file:
            encoded = base64.b64encode(file.read()).decode('utf-8')
            
            # Determine MIME type based on file extension
            if file_ext == '.pdf':
                return f"data:application/pdf;base64,{encoded}"
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                mime_type = 'image/png' if file_ext == '.png' else 'image/jpeg'
                return f"data:{mime_type};base64,{encoded}"
            else:
                # Default to PNG for unknown image types
                return f"data:image/png;base64,{encoded}"
    
    def process_file(self, file_path):
        """Process image or PDF file with Mistral OCR"""
        print(f"Processing file: {file_path}")
        
        # Encode file (image or PDF)
        base64_file = self.encode_file(file_path)
        
        # Prepare request
        url = f"{self.endpoint}/v1/ocr"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Determine document type based on file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext == '.pdf':
            payload = {
                "model": self.model_name,
                "document": {
                    "type": "document_url",
                    "document_url": base64_file
                }
            }
        else:
            payload = {
                "model": self.model_name,
                "document": {
                    "type": "image_url",
                    "image_url": base64_file
                }
            }
        
        # Make request with timeout
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            raise Exception(f"OCR request failed: {response.status_code} - {response.text}")
    
    def extract_text(self, file_path):
        """Extract markdown content from image or PDF file"""
        result = self.process_file(file_path)
        
        # Extract markdown from the response structure
        try:
            if 'pages' in result and len(result['pages']) > 0:
                # For multi-page documents (PDFs), combine all pages
                all_markdown = []
                for i, page in enumerate(result['pages']):
                    markdown_content = page.get('markdown', '')
                    if markdown_content.strip():
                        # Add page number for multi-page documents
                        if len(result['pages']) > 1:
                            page_header = f"\n\n## Page {i + 1}\n\n"
                            all_markdown.append(page_header + markdown_content)
                        else:
                            all_markdown.append(markdown_content)
                
                # Join all pages
                combined_markdown = '\n\n'.join(all_markdown)
                return combined_markdown
            else:
                # Fallback: return the full result as JSON if structure is unexpected
                return json.dumps(result, indent=2)
        except (KeyError, IndexError, TypeError) as e:
            # If there's any issue parsing, return the raw JSON
            print(f"Warning: Could not extract markdown, returning raw response: {e}")
            return json.dumps(result, indent=2)

    def process_image(self, image_path):
        """Backward compatibility: alias for process_file"""
        return self.process_file(image_path)


def main():
    """Test the simple OCR"""
    try:
        # Initialize OCR
        ocr = SimpleOCR()
        print("✅ Simple OCR initialized")
        
        # Test with a sample image (you can put any image here)
        test_image = "test_image.jpg"  # Put your test image here
        
        if Path(test_image).exists():
            print(f"\n📷 Processing {test_image}...")
            
            # Extract text
            text = ocr.extract_text(test_image)
            
            print("\n📝 Extracted text:")
            print("-" * 50)
            print(text)
            print("-" * 50)
            
            # Save result
            output_file = "ocr_result.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n💾 Result saved to: {output_file}")
            
        else:
            print(f"❌ Test image not found: {test_image}")
            print("Put a test image in the current directory and update the filename in the script")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()