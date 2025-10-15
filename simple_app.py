"""
Simple Streamlit app for Mistral OCR
"""
import streamlit as st
import tempfile
import os
from PIL import Image
from simple_ocr import SimpleOCR

st.set_page_config(
    page_title="Simple Mistral OCR",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Simple Mistral OCR")
st.markdown("Upload an image or PDF to extract text using Mistral OCR model")

# Initialize OCR
@st.cache_resource
def get_ocr():
    try:
        return SimpleOCR()
    except Exception as e:
        st.error(f"Failed to initialize OCR: {e}")
        return None

ocr = get_ocr()

if ocr:
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image or PDF file",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Upload an image (PNG, JPG, JPEG) or PDF file to extract text"
    )
    
    if uploaded_file is not None:
        # Display image
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Uploaded File")
            
            # Check if it's a PDF or image
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                st.info("📄 PDF file uploaded")
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size:,} bytes")
            else:
                # Display image
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)
        
        with col2:
            st.subheader("📝 Extracted Text")
            
            if st.button("Extract Text", type="primary"):
                with st.spinner("Processing file..."):
                    try:
                        # Save uploaded file temporarily
                        file_extension = uploaded_file.name.lower().split('.')[-1]
                        
                        if file_extension == 'pdf':
                            # Handle PDF files - save directly
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                                tmp_file.write(uploaded_file.read())
                                tmp_path = tmp_file.name
                        else:
                            # Handle image files
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                                # Convert and save as PNG
                                if image.mode != 'RGB':
                                    image = image.convert('RGB')
                                image.save(tmp_file.name, 'PNG')
                                tmp_path = tmp_file.name
                        
                        # Extract text
                        extracted_text = ocr.extract_text(tmp_path)
                        
                        # Save to markdown file
                        output_filename = f"extracted_text_{uploaded_file.name.split('.')[0]}.md"
                        with open(output_filename, 'w', encoding='utf-8') as f:
                            f.write(extracted_text)
                        
                        # Clean up temp file
                        os.unlink(tmp_path)
                        
                        # Display result
                        st.success(f"✅ Text extracted and saved to: `{output_filename}`")
                        st.text_area(
                            "Extracted Text:",
                            value=extracted_text,
                            height=400,
                            help="Copy this text or download it below"
                        )
                        
                        # Download buttons
                        col_dl1, col_dl2 = st.columns(2)
                        with col_dl1:
                            st.download_button(
                                label="📥 Download as TXT",
                                data=extracted_text,
                                file_name=f"extracted_text_{uploaded_file.name.split('.')[0]}.txt",
                                mime="text/plain"
                            )
                        with col_dl2:
                            st.download_button(
                                label="📄 Download as MD",
                                data=extracted_text,
                                file_name=output_filename,
                                mime="text/markdown"
                            )
                        
                    except Exception as e:
                        st.error(f"Error processing file: {e}")
    
    else:
        st.info("👆 Upload an image or PDF file to get started")
        
        # Example
        st.markdown("### Example Usage")
        st.markdown("""
        1. Upload a PNG, JPG, JPEG, or PDF file
        2. Click "Extract Text" 
        3. View and download the extracted text
        
        **Supported formats:** 
        - **Images:** PNG, JPG, JPEG
        - **Documents:** PDF (single or multi-page)
        
        **Content types:** Documents, invoices, receipts, handwritten notes, forms, etc.
        """)

else:
    st.error("❌ OCR not available. Check your environment variables.")
    st.info("""
    Make sure your `.env` file contains:
    ```
    MISTRAL_OCR_ENDPOINT=your_endpoint_here
    MISTRAL_OCR_KEY=your_key_here
    ```
    """)