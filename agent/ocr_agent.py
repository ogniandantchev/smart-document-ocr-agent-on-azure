"""
Document OCR Agent using Microsoft Agent Framework with Mistral OCR Tool
"""
import os
import base64
import asyncio
from typing import Optional, Union, List, Dict, Any
from io import BytesIO
from PIL import Image

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, AzureCliCredential

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from agent_framework.telemetry import setup_telemetry


class MistralOCRTool:
    """OCR Tool using Mistral OCR model for the Agent Framework"""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        model_name: str = "mistral-ocr-2503"
    ):
        """
        Initialize the Mistral OCR Tool
        
        Args:
            endpoint: Mistral OCR endpoint URL
            api_key: API key for authentication
            model_name: Model identifier
        """
        self.endpoint = endpoint
        self.model_name = model_name
        
        # Initialize Mistral OCR client
        self.ocr_client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
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
    
    async def extract_text_from_image(
        self,
        image_path: str,
        extract_tables: bool = True,
        preserve_formatting: bool = True,
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Extract text from an image using Mistral OCR
        
        Args:
            image_path: Path to the image file
            extract_tables: Whether to extract tables in markdown format
            preserve_formatting: Whether to preserve document formatting
            custom_instructions: Custom instructions for OCR processing
            
        Returns:
            Extracted text in markdown format
        """
        # Default system prompt optimized for OCR
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
        
        # Add custom instructions if provided
        if custom_instructions:
            system_prompt += f"\n- Additional instructions: {custom_instructions}"
        
        # Encode image
        base64_image = self._encode_image(image_path)
        
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
        
        return markdown_content
    
    async def extract_text_from_multiple_images(
        self,
        image_paths: List[str],
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Extract text from multiple images and combine them
        
        Args:
            image_paths: List of image file paths
            custom_instructions: Custom instructions for OCR processing
            
        Returns:
            Combined extracted text in markdown format
        """
        all_pages_markdown = []
        
        for i, image_path in enumerate(image_paths, 1):
            try:
                result = await self.extract_text_from_image(
                    image_path, 
                    custom_instructions=custom_instructions
                )
                all_pages_markdown.append(f"## Page {i}\n\n{result}")
            except Exception as e:
                all_pages_markdown.append(f"## Page {i}\n\nError processing image: {str(e)}")
        
        combined_markdown = "\n\n---\n\n".join(all_pages_markdown)
        return combined_markdown


class DocumentOCRAgent:
    """AI Agent for document OCR using Microsoft Agent Framework with Mistral OCR"""
    
    def __init__(
        self,
        mistral_endpoint: str,
        mistral_api_key: str,
        mistral_model_name: str = "mistral-ocr-2503",
        azure_ai_credential: Optional[Any] = None,
        agent_instructions: Optional[str] = None
    ):
        """
        Initialize the OCR Agent with Agent Framework
        
        Args:
            mistral_endpoint: Mistral OCR endpoint URL
            mistral_api_key: Mistral API key for authentication
            mistral_model_name: Mistral model identifier
            azure_ai_credential: Azure credential for the agent client
            agent_instructions: Custom instructions for the agent
        """
        self.mistral_endpoint = mistral_endpoint
        self.mistral_api_key = mistral_api_key
        self.mistral_model_name = mistral_model_name
        
        # Initialize Mistral OCR Tool
        self.ocr_tool = MistralOCRTool(
            endpoint=mistral_endpoint,
            api_key=mistral_api_key,
            model_name=mistral_model_name
        )
        
        # Set up credential
        if azure_ai_credential is None:
            azure_ai_credential = AzureCliCredential()
        self.credential = azure_ai_credential
        
        # Default agent instructions
        if agent_instructions is None:
            agent_instructions = """You are a helpful document OCR assistant. I can help you extract text from images and documents using advanced OCR technology.

My capabilities include:
- Extracting text from images (JPEG, PNG, PDF pages)
- Converting documents to markdown format
- Preserving formatting, tables, and structure
- Processing multiple pages at once
- Handling various document types (invoices, reports, forms, etc.)

When you provide an image or ask me to process a document, I'll use my OCR tool to extract the text and provide it to you in a well-formatted markdown structure.

How can I help you with document processing today?"""
        
        self.agent_instructions = agent_instructions
        self.agent = None
    
    async def _create_agent(self) -> ChatAgent:
        """Create and configure the Agent Framework agent with OCR tools"""
        
        # Create OCR tool functions for the agent
        async def extract_text_from_image(
            image_path: str,
            extract_tables: bool = True,
            preserve_formatting: bool = True,
            custom_instructions: str = None
        ) -> str:
            """
            Extract text from an image using OCR
            
            Args:
                image_path: Path to the image file to process
                extract_tables: Whether to extract tables in markdown format (default: True)
                preserve_formatting: Whether to preserve document formatting (default: True)
                custom_instructions: Additional instructions for text extraction
                
            Returns:
                Extracted text in markdown format
            """
            return await self.ocr_tool.extract_text_from_image(
                image_path=image_path,
                extract_tables=extract_tables,
                preserve_formatting=preserve_formatting,
                custom_instructions=custom_instructions
            )
        
        async def extract_text_from_multiple_images(
            image_paths: str,  # Will be parsed as comma-separated list
            custom_instructions: str = None
        ) -> str:
            """
            Extract text from multiple images and combine them
            
            Args:
                image_paths: Comma-separated list of image file paths
                custom_instructions: Additional instructions for text extraction
                
            Returns:
                Combined extracted text in markdown format
            """
            # Parse comma-separated paths
            paths_list = [path.strip() for path in image_paths.split(',')]
            return await self.ocr_tool.extract_text_from_multiple_images(
                image_paths=paths_list,
                custom_instructions=custom_instructions
            )
        
        # Create Azure AI Agent Client
        chat_client = AzureAIAgentClient(async_credential=self.credential)
        
        # Create agent with OCR tools
        agent = chat_client.create_agent(
            name="DocumentOCRAgent",
            instructions=self.agent_instructions,
            tools=[extract_text_from_image, extract_text_from_multiple_images]
        )
        
        return agent
    
    async def process_document(
        self,
        message: str,
        image_path: Optional[str] = None
    ) -> str:
        """
        Process a document OCR request through the agent
        
        Args:
            message: User message or question
            image_path: Optional image path to process
            
        Returns:
            Agent response
        """
        if self.agent is None:
            self.agent = await self._create_agent()
        
        # Construct the full message
        if image_path:
            full_message = f"{message}\n\nPlease process this image: {image_path}"
        else:
            full_message = message
        
        # Get agent response
        response = await self.agent.run(full_message)
        return response
    
    async def chat(self, message: str) -> str:
        """
        Simple chat interface with the OCR agent
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        if self.agent is None:
            self.agent = await self._create_agent()
        
        response = await self.agent.run(message)
        return response


def setup_observability(enable_sensitive_data: bool = True):
    """Set up OpenTelemetry tracing for the OCR Agent"""
    setup_telemetry(
        otlp_endpoint="http://localhost:4317",  # AI Toolkit gRPC endpoint
        enable_sensitive_data=enable_sensitive_data  # Enable capturing prompts and completions
    )


async def create_ocr_agent_from_env() -> DocumentOCRAgent:
    """
    Create OCR Agent using environment variables
    
    Returns:
        Configured DocumentOCRAgent instance
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    # Mistral OCR configuration
    mistral_endpoint = os.getenv("MISTRAL_OCR_ENDPOINT")
    mistral_api_key = os.getenv("MISTRAL_OCR_KEY")
    mistral_model_name = os.getenv("MISTRAL_OCR_MODEL_NAME", "mistral-ocr-2503")
    
    if not mistral_endpoint or not mistral_api_key:
        raise ValueError(
            "Missing required environment variables: MISTRAL_OCR_ENDPOINT and MISTRAL_OCR_KEY"
        )
    
    # Set up observability
    setup_observability()
    
    return DocumentOCRAgent(
        mistral_endpoint=mistral_endpoint,
        mistral_api_key=mistral_api_key,
        mistral_model_name=mistral_model_name
    )


# Example usage and testing
async def main():
    """Example usage of the OCR Agent"""
    try:
        # Create agent from environment variables
        agent = await create_ocr_agent_from_env()
        
        # Example 1: Chat with the agent
        print("=== OCR Agent Chat ===")
        response = await agent.chat("Hello! What can you help me with?")
        print(f"Agent: {response}")
        
        # Example 2: Process a specific document (if path provided)
        # response = await agent.process_document(
        #     "Please extract all text from this document",
        #     image_path="/path/to/your/document.jpg"
        # )
        # print(f"Agent: {response}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())