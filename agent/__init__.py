"""
Azure AI Document OCR Agent Package
"""
from .ocr_agent import DocumentOCRAgent, create_ocr_agent_from_env

__version__ = "1.0.0"
__all__ = ["DocumentOCRAgent", "create_ocr_agent_from_env"]