"""
Translation service for coordinating text translation.
"""
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Service for coordinating text translation operations.
    """
    
    def __init__(self, translation_model):
        """
        Initialize the translation service.
        
        Args:
            translation_model: Translation model instance
        """
        self.translation_model = translation_model
    
    def translate(self, text, source_lang='auto', target_lang='en'):
        """
        Translate text from source language to target language.
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code (or 'auto' for detection)
            target_lang (str): Target language code
            
        Returns:
            str: Translated text
        """
        if not text or not text.strip():
            return text
            
        # Detect language if set to auto
        if source_lang == 'auto':
            detected_lang = self.detect_language(text)
            logger.info(f"Detected language: {detected_lang}")
            source_lang = detected_lang
            
        # No need to translate if source and target are the same
        if source_lang == target_lang:
            return text
            
        # Translate the text
        translated = self.translation_model.translate(
            text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        return translated
    
    def detect_language(self, text):
        """
        Detect the language of the input text.
        
        Args:
            text (str): Text to detect language for
            
        Returns:
            str: ISO language code (e.g., 'en')
        """
        return self.translation_model.detect_language(text)
    
    def get_supported_languages(self):
        """
        Get a list of supported language codes.
        
        Returns:
            list: List of supported language codes
        """
        return self.translation_model.get_supported_languages()