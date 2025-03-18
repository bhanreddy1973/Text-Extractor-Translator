"""
Text extraction service coordinating OCR and ML enhancement.
"""
import os
import time
from PIL import Image
import cv2
import numpy as np
import logging
from services.nlp_processing import NLPProcessor

logger = logging.getLogger(__name__)

class TextExtractionService:
    """
    Service for coordinating text extraction from documents and images.
    """
    
    def __init__(self, ocr_model, ml_model, preprocessor):
        """
        Initialize the text extraction service.
        
        Args:
            ocr_model: OCR model instance
            ml_model: ML enhancement model instance
            preprocessor: Image preprocessor instance
        """
        self.ocr_model = ocr_model
        self.ml_model = ml_model
        self.preprocessor = preprocessor
        self.nlp_processor = NLPProcessor()
        
        # File type handlers
        self.file_handlers = {
            'pdf': self._handle_pdf,
            'image': self._handle_image,
        }
    
    def extract_text(self, file_path, source_lang='auto', enhance=True):
        """
        Extract text from a file.
        
        Args:
            file_path (str): Path to the file
            source_lang (str): Source language code (or 'auto' for detection)
            enhance (bool): Whether to apply ML enhancement
            
        Returns:
            tuple: (extracted_text, confidence_score)
        """
        start_time = time.time()
        
        # Determine file type
        file_type = self._determine_file_type(file_path)
        
        # Extract text based on file type
        if file_type in self.file_handlers:
            text, confidence = self.file_handlers[file_type](file_path, source_lang)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return "Unsupported file type", 0.0
        
        # Apply ML enhancement if requested
        if enhance and self.ml_model:
            text, confidence = self.ml_model.enhance_text(text, confidence)
        
        # Apply NLP processing
        text = self.nlp_processor.process_text(text)
        
        processing_time = time.time() - start_time
        logger.info(f"Text extraction completed in {processing_time:.2f} seconds with confidence {confidence:.2f}")
        
        return text, confidence
    
    def _determine_file_type(self, file_path):
        """
        Determine the type of file based on extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File type ('pdf' or 'image')
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']:
            return 'image'
        else:
            return 'unknown'
    
    def _handle_pdf(self, file_path, lang):
        """
        Handle text extraction from PDF files.
        
        Args:
            file_path (str): Path to the PDF file
            lang (str): Language code
            
        Returns:
            tuple: (extracted_text, confidence_score)
        """
        return self.ocr_model.extract_text_from_pdf(file_path, lang)
    
    def _handle_image(self, file_path, lang):
        """
        Handle text extraction from image files.
        
        Args:
            file_path (str): Path to the image file
            lang (str): Language code
            
        Returns:
            tuple: (extracted_text, confidence_score)
        """
        try:
            # Load image
            image = Image.open(file_path)
            
            # Preprocess image
            preprocessed = self.preprocessor.preprocess(image)
            
            # Deskew image if needed
            deskewed = self.preprocessor.deskew(preprocessed)
            
            # Extract text using OCR
            text, confidence = self.ocr_model.extract_text_from_image(deskewed, lang)
            
            return text, confidence
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return "Image processing failed", 0.0