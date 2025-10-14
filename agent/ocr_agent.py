"""
Document OCR Agent using Mistral OCR on Azure AI Foundry
"""
import os
import base64
from typing import Optional
from io import BytesIO
from PIL import Image

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import Agent, AgentThread


class DocumentOCRAgent:
    """AI Agent for document OCR using Mistral OCR model"""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        model_name: str = "mistral-ocr-2503",
        project_connection_string: Optional[str] = None
    ):
        """
        Initialize the OCR Agent
        
        Args:
            endpoint: Mistral OCR endpoint URL
            api_key: API key for authentication
            model_name: Model identifier
            project_connection_string: Azure AI Project connection string (optional)
        """
        self.endpoint = endpoint
        self.model_name = model_name
        
        # Initialize Mistral OCR client
        self.ocr_client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )
        
        # Initialize Azure AI Project client if connection string provided
        self.project_client = None
        if project_connection_string:
            self.project_client = AIProjectClient.from_connection_string(
                credential=DefaultAzureCredential(),
                conn_str=project_connection_string
            )
    
    def _encode_image(self, image_input) -> str:
        """
        Encode image to base64 string
        
        Args:
            image_input: File path, bytes, or PIL Image
            
        Returns:
            Base64 encoded image string
        """
        if isinstance(image_input, str):
            # File path
            with open(image_input, "rb") as f:
                image_bytes = f.read()
        elif isinstance(image_input, bytes):
            # Raw bytes
            image_bytes = image_input
        elif isinstance(image_input, Image.Image):
            # PIL Image
            buffer = BytesIO()
            image_input.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
        else:
            raise ValueError("Unsupported image input type")
        
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def process_document(
        self,
        image_input,
        system_prompt: Optional[str] = None,
        extract_tables: bool = True,
        preserve_formatting: bool = True
    ) -> dict:
        """
        Process document image and extract text as markdown
        
        Args:
            image_input: Image file path, bytes, or PIL Image
            system_prompt: Custom system prompt (optional)
            extract_tables: Whether to extract tables in markdown format
            preserve_formatting: Whether to preserve document formatting
            
        Returns:
            Dictionary with markdown content and metadata
        """
        # Default system prompt optimized for OCR
        if system_prompt is None:
            system_prompt = """You are an expert OCR system. Convert the provided document image to detailed markdown format.

Instructions:
- Extract ALL text content accurately
- Preserve document structure and formatting
- Use appropriate markdown headers (# ## ###)
- Format tables using markdown table syntax
- Preserve lists, bullet points, and numbering
- Include any metadata or special formatting
- Be thorough and precise"""
        
        # Add specific instructions based on parameters
        if extract_tables:
            system_prompt += "\n- Pay special attention to tables and format them correctly in markdown"
        if preserve_formatting:
            system_prompt += "\n- Maintain the original document's visual hierarchy and structure"
        
        # Encode image
        base64_image = self._encode_image(image_input)
        
        # Prepare messages for Mistral OCR
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Please convert this document to detailed markdown format."
                    }
                ]
            }
        ]
        
        # Call Mistral OCR
        response = self.ocr_client.complete(
            messages=messages,
            model=self.model_name,
            temperature=0.0,  # Deterministic for OCR
            max_tokens=4096
        )
        
        # Extract markdown content
        markdown_content = response.choices[0].message.content
        
        return {
            "markdown": markdown_content,
            "model": self.model_name,
            "tokens_used": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        }
    
    def process_multi_page_document(
        self,
        image_inputs: list,
        system_prompt: Optional[str] = None
    ) -> dict:
        """
        Process multiple pages of a document
        
        Args:
            image_inputs: List of image inputs (file paths, bytes, or PIL Images)
            system_prompt: Custom system prompt (optional)
            
        Returns:
            Dictionary with combined markdown content and metadata
        """
        all_pages_markdown = []
        total_tokens = {"prompt": 0, "completion": 0, "total": 0}
        
        for i, image_input in enumerate(image_inputs, 1):
            result = self.process_document(image_input, system_prompt)
            all_pages_markdown.append(f"## Page {i}\n\n{result['markdown']}")
            
            # Accumulate token usage
            for key in total_tokens:
                total_tokens[key] += result["tokens_used"][key]
        
        combined_markdown = "\n\n---\n\n".join(all_pages_markdown)
        
        return {
            "markdown": combined_markdown,
            "model": self.model_name,
            "pages_processed": len(image_inputs),
            "tokens_used": total_tokens
        }


def create_ocr_agent_from_env() -> DocumentOCRAgent:
    """
    Create OCR Agent using environment variables
    
    Returns:
        Configured DocumentOCRAgent instance
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    endpoint = os.getenv("MISTRAL_OCR_ENDPOINT")
    api_key = os.getenv("MISTRAL_OCR_KEY")
    model_name = os.getenv("MISTRAL_OCR_MODEL_NAME", "mistral-ocr-2503")
    
    if not endpoint or not api_key:
        raise ValueError(
            "Missing required environment variables: MISTRAL_OCR_ENDPOINT and MISTRAL_OCR_KEY"
        )
    
    # Optional: AI Project connection string
    project_conn_str = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
    
    return DocumentOCRAgent(
        endpoint=endpoint,
        api_key=api_key,
        model_name=model_name,
        project_connection_string=project_conn_str
    )