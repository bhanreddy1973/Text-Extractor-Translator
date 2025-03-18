"""
OCR model implementation using Tesseract.
"""
import os
import pytesseract
from PIL import Image
import pdfplumber
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

class OCRModel:
    """
    Optical Character Recognition model using Tesseract OCR.
    """
    
    def __init__(self, tesseract_cmd=None, lang='eng'):
        """
        Initialize the OCR model.
        
        Args:
            tesseract_cmd (str, optional): Path to Tesseract executable.
            lang (str, optional): Default language for OCR. Defaults to 'eng'.
        """
        self.lang = lang
        self.language_mapping = {
            'en': 'eng',     'es': 'spa',     'fr': 'fra',
            'de': 'deu',     'it': 'ita',     'pt': 'por',
            'nl': 'nld',     'ru': 'rus',     'zh': 'chi_sim+chi_tra',
            'ja': 'jpn',     'ko': 'kor',     'ar': 'ara',
            'hi': 'hin',     'bn': 'ben',     'pa': 'pan',
            'te': 'tel',     'ta': 'tam',     'ur': 'urd',
            'fa': 'fas',     'tr': 'tur',     'pl': 'pol',
            'uk': 'ukr',     'vi': 'vie',     'th': 'tha',
            'id': 'ind'
        }
        
        # Set Tesseract command if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            
        # Verify Tesseract installation
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR initialized successfully")
        except Exception as e:
            logger.error(f"Tesseract OCR initialization failed: {str(e)}")
            raise RuntimeError("Tesseract OCR not properly installed or configured")
    
    def extract_text_from_image(self, image, lang=None):
        """
        Extract text from an image using Tesseract OCR.
        
        Args:
            image: PIL Image or numpy array
            lang (str, optional): Language code for OCR.
        
        Returns:
            tuple: (extracted_text, confidence_score)
        """
        # Convert numpy array to PIL Image if needed
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Use provided language or default
        ocr_lang = self._map_language_code(lang) if lang else self.lang
        
        # Extract text with confidence data
        data = pytesseract.image_to_data(image, lang=ocr_lang, output_type=pytesseract.Output.DICT)
        
        # Extract text and calculate mean confidence
        full_text = ' '.join([word for word in data['text'] if word.strip()])
        
        # Calculate confidence score from valid confidence values
        confidences = [conf for conf, text in zip(data['conf'], data['text']) 
                      if text.strip() and conf != -1]
        
        confidence_score = np.mean(confidences) / 100 if confidences else 0.0
        
        return full_text, confidence_score
    
    def extract_text_from_pdf(self, pdf_path, lang=None):
        """
        Extract text from a PDF document.
        
        Args:
            pdf_path (str): Path to PDF file.
            lang (str, optional): Language code for OCR.
        
        Returns:
            tuple: (extracted_text, confidence_score)
        """
        extracted_texts = []
        confidence_scores = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Try to extract text directly first (if PDF has text layer)
                text = page.extract_text()
                
                if text and text.strip():
                    # Text layer exists, assign high confidence
                    extracted_texts.append(text)
                    confidence_scores.append(0.95)  # High confidence for native text
                else:
                    # No text layer, perform OCR on page image
                    img = page.to_image().original
                    page_text, page_conf = self.extract_text_from_image(img, lang)
                    extracted_texts.append(page_text)
                    confidence_scores.append(page_conf)
        
        # Combine all extracted text
        full_text = '\n\n'.join(extracted_texts)
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        return full_text, avg_confidence
    
    def _map_language_code(self, lang_code):
        """
        Map ISO language code to Tesseract language code.
        
        Args:
            lang_code (str): ISO language code (e.g., 'en')
        
        Returns:
            str: Tesseract language code (e.g., 'eng')
        """
        if lang_code == 'auto':
            return 'eng'  # Default to English for auto detection
            
        return self.language_mapping.get(lang_code, 'eng')