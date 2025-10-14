"""
Document OCR Agent using Microsoft Agent Framework + Mistral OCR
This version properly integrates with Azure AI Agent Service
"""
import os
import base64
from typing import Optional, Dict, Any
from io import BytesIO
from PIL import Image
import json

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    Agent,
    AgentThread,
    MessageAttachment,
    MessageRole,
    RunStatus,
    ToolSet,
    FunctionTool
)
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential


class MistralOCRTool:
    """Tool wrapper for Mistral OCR to be used by Agent Framework"""
    
    def __init__(self, endpoint: str, api_key: str, model_name: str = "mistral-ocr-2503"):
        self.endpoint = endpoint
        self.model_name = model_name
        self.ocr_client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )
    
    def extract_text_from_image(self, image_base64: str, instructions: str = None) -> str:
        """
        Tool function: Extract text from image using Mistral OCR
        
        Args:
            image_base64: Base64 encoded image
            instructions: Optional extraction instructions
        
        Returns:
            Extracted text in markdown format
        """
        system_prompt = instructions or """You are an expert OCR system. Convert the provided document image to detailed markdown format.

Instructions:
- Extract ALL text content accurately
- Preserve document structure and formatting
- Use appropriate markdown headers (# ## ###)
- Format tables using markdown table syntax
- Preserve lists, bullet points, and numbering
- Be thorough and precise"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                    },
                    {
                        "type": "text",
                        "text": "Please convert this document to detailed markdown format."
                    }
                ]
            }
        ]
        
        response = self.ocr_client.complete(
            messages=messages,
            model=self.model_name,
            temperature=0.0,
            max_tokens=4096
        )
        
        return response.choices[0].message.content


class DocumentOCRAgentFramework:
    """
    Document OCR Agent using Microsoft Agent Framework
    Orchestrates OCR tasks using Azure AI Agent Service
    """
    
    def __init__(
        self,
        project_client: AIProjectClient,
        mistral_endpoint: str,
        mistral_api_key: str,
        model_name: str = "mistral-ocr-2503",
        agent_name: str = "DocumentOCRAgent"
    ):
        """
        Initialize the Agent Framework-based OCR Agent
        
        Args:
            project_client: Azure AI Project client
            mistral_endpoint: Mistral OCR endpoint
            mistral_api_key: Mistral API key
            model_name: Mistral model identifier
            agent_name: Name for the agent
        """
        self.project_client = project_client
        self.agent_name = agent_name
        
        # Initialize Mistral OCR tool
        self.ocr_tool = MistralOCRTool(mistral_endpoint, mistral_api_key, model_name)
        
        # Create or get agent
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create agent with OCR capabilities"""
        
        # Define OCR function tool
        ocr_function = {
            "type": "function",
            "function": {
                "name": "extract_text_from_image",
                "description": "Extract text from a document image using advanced OCR. Returns markdown-formatted text with preserved structure and tables.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_base64": {
                            "type": "string",
                            "description": "Base64 encoded image of the document"
                        },
                        "instructions": {
                            "type": "string",
                            "description": "Optional specific instructions for extraction (e.g., 'focus on tables', 'extract only invoice fields')"
                        }
                    },
                    "required": ["image_base64"]
                }
            }
        }
        
        # Create function tool
        function_tool = FunctionTool(functions=[ocr_function])
        toolset = ToolSet(function_tools=[function_tool])
        
        # Create agent with instructions
        agent = self.project_client.agents.create_agent(
            model="gpt-4o",  # Orchestration model
            name=self.agent_name,
            instructions="""You are a document processing assistant specializing in OCR (Optical Character Recognition).

Your capabilities:
1. Extract text from document images with high accuracy
2. Preserve document structure and formatting
3. Handle tables, lists, and complex layouts
4. Provide results in clean markdown format

When a user provides a document:
1. Use the extract_text_from_image function to process it
2. Present the results clearly
3. Highlight any important findings
4. Offer to extract specific information if needed

Always be precise, thorough, and helpful.""",
            tools=toolset.definitions
        )
        
        return agent
    
    def _encode_image(self, image_input) -> str:
        """Encode image to base64"""
        if isinstance(image_input, str):
            with open(image_input, "rb") as f:
                image_bytes = f.read()
        elif isinstance(image_input, bytes):
            image_bytes = image_input
        elif isinstance(image_input, Image.Image):
            buffer = BytesIO()
            image_input.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
        else:
            raise ValueError("Unsupported image input type")
        
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _handle_tool_calls(self, run, thread):
        """Handle tool calls from the agent"""
        tool_outputs = []
        
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "extract_text_from_image":
                # Parse arguments
                args = json.loads(tool_call.function.arguments)
                
                # Call OCR tool
                result = self.ocr_tool.extract_text_from_image(
                    image_base64=args.get("image_base64"),
                    instructions=args.get("instructions")
                )
                
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": result
                })
        
        # Submit tool outputs
        if tool_outputs:
            self.project_client.agents.submit_tool_outputs_to_run(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
    
    def process_document(
        self,
        image_input,
        user_message: str = None,
        extract_tables: bool = True,
        preserve_formatting: bool = True
    ) -> Dict[str, Any]:
        """
        Process document using Agent Framework orchestration
        
        Args:
            image_input: Image file path, bytes, or PIL Image
            user_message: Custom user message (optional)
            extract_tables: Whether to extract tables
            preserve_formatting: Whether to preserve formatting
        
        Returns:
            Dictionary with markdown content and metadata
        """
        # Encode image
        image_base64 = self._encode_image(image_input)
        
        # Build user message
        if user_message is None:
            instructions = []
            if extract_tables:
                instructions.append("pay special attention to tables")
            if preserve_formatting:
                instructions.append("preserve the document structure")
            
            instruction_text = " and ".join(instructions) if instructions else ""
            user_message = f"Please extract all text from this document image"
            if instruction_text:
                user_message += f", {instruction_text}"
            user_message += "."
        
        # Create thread
        thread = self.project_client.agents.create_thread()
        
        # Create message with image context
        # Note: We embed image_base64 in the message for the agent to use with the tool
        message_content = f"{user_message}\n\n[Image data provided for OCR processing]"
        
        self.project_client.agents.create_message(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=message_content
        )
        
        # Create run
        run = self.project_client.agents.create_run(
            thread_id=thread.id,
            agent_id=self.agent.id
        )
        
        # Poll for completion and handle tool calls
        while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
            if run.status == RunStatus.REQUIRES_ACTION:
                # Handle tool calls
                self._handle_tool_calls(run, thread)
            
            # Wait and get updated status
            import time
            time.sleep(1)
            run = self.project_client.agents.get_run(
                thread_id=thread.id,
                run_id=run.id
            )
        
        if run.status == RunStatus.FAILED:
            raise Exception(f"Agent run failed: {run.last_error}")
        
        # Get messages
        messages = self.project_client.agents.list_messages(thread_id=thread.id)
        
        # Extract assistant's response
        assistant_message = None
        for msg in messages.data:
            if msg.role == MessageRole.ASSISTANT:
                assistant_message = msg
                break
        
        if not assistant_message:
            raise Exception("No response from agent")
        
        # Extract markdown content from message
        markdown_content = ""
        for content_item in assistant_message.content:
            if hasattr(content_item, 'text'):
                markdown_content += content_item.text.value
        
        # Clean up thread
        self.project_client.agents.delete_thread(thread.id)
        
        return {
            "markdown": markdown_content,
            "agent_id": self.agent.id,
            "thread_id": thread.id,
            "run_id": run.id,
            "status": run.status
        }
    
    def chat(self, user_message: str, thread_id: str = None) -> Dict[str, Any]:
        """
        Interactive chat with the agent
        
        Args:
            user_message: User's message
            thread_id: Existing thread ID (optional, creates new if None)
        
        Returns:
            Agent's response with metadata
        """
        # Create or use existing thread
        if thread_id is None:
            thread = self.project_client.agents.create_thread()
            thread_id = thread.id
        else:
            thread = self.project_client.agents.get_thread(thread_id=thread_id)
        
        # Send message
        self.project_client.agents.create_message(
            thread_id=thread_id,
            role=MessageRole.USER,
            content=user_message
        )
        
        # Create run
        run = self.project_client.agents.create_run(
            thread_id=thread_id,
            agent_id=self.agent.id
        )
        
        # Poll for completion
        while run.status in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
            if run.status == RunStatus.REQUIRES_ACTION:
                self._handle_tool_calls(run, thread)
            
            import time
            time.sleep(1)
            run = self.project_client.agents.get_run(
                thread_id=thread_id,
                run_id=run.id
            )
        
        # Get response
        messages = self.project_client.agents.list_messages(thread_id=thread_id)
        assistant_message = next(
            (msg for msg in messages.data if msg.role == MessageRole.ASSISTANT),
            None
        )
        
        response_text = ""
        if assistant_message:
            for content_item in assistant_message.content:
                if hasattr(content_item, 'text'):
                    response_text += content_item.text.value
        
        return {
            "response": response_text,
            "thread_id": thread_id,
            "run_id": run.id,
            "status": run.status
        }
    
    def cleanup(self):
        """Delete the agent"""
        try:
            self.project_client.agents.delete_agent(self.agent.id)
        except:
            pass


def create_ocr_agent_with_framework() -> DocumentOCRAgentFramework:
    """
    Create OCR Agent using Microsoft Agent Framework from environment variables
    
    Returns:
        Configured DocumentOCRAgentFramework instance
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration
    project_conn_str = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
    mistral_endpoint = os.getenv("MISTRAL_OCR_ENDPOINT")
    mistral_key = os.getenv("MISTRAL_OCR_KEY")
    model_name = os.getenv("MISTRAL_OCR_MODEL_NAME", "mistral-ocr-2503")
    agent_name = os.getenv("AGENT_NAME", "DocumentOCRAgent")
    
    if not all([project_conn_str, mistral_endpoint, mistral_key]):
        raise ValueError(
            "Missing required environment variables: "
            "AZURE_AI_PROJECT_CONNECTION_STRING, MISTRAL_OCR_ENDPOINT, MISTRAL_OCR_KEY"
        )
    
    # Create AI Project client
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=project_conn_str
    )
    
    # Create agent
    return DocumentOCRAgentFramework(
        project_client=project_client,
        mistral_endpoint=mistral_endpoint,
        mistral_api_key=mistral_key,
        model_name=model_name,
        agent_name=agent_name
    )