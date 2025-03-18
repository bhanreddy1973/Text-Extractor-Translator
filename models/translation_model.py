"""
Translation model implementation using multiple services.
"""
import os
from google.cloud import translate_v2 as translate
import deepl
from langdetect import detect
import logging

logger = logging.getLogger(__name__)

class TranslationModel:
    """
    Translation model that integrates multiple translation services
    with fallback mechanisms.
    """
    
    def __init__(self, google_api_key=None, deepl_api_key=None):
        """
        Initialize the translation model with available API keys.
        
        Args:
            google_api_key (str, optional): Google Translate API key.
            deepl_api_key (str, optional): DeepL API key.
        """
        self.google_client = None
        self.deepl_client = None
        self.language_mapping = {
            'en': {'google': 'en', 'deepl': 'EN'},
            'es': {'google': 'es', 'deepl': 'ES'},
            'fr': {'google': 'fr', 'deepl': 'FR'},
            'de': {'google': 'de', 'deepl': 'DE'},
            'it': {'google': 'it', 'deepl': 'IT'},
            'pt': {'google': 'pt', 'deepl': 'PT'},
            'nl': {'google': 'nl', 'deepl': 'NL'},
            'ru': {'google': 'ru', 'deepl': 'RU'},
            'zh': {'google': 'zh', 'deepl': 'ZH'},
            'ja': {'google': 'ja', 'deepl': 'JA'},
            # Add more languages as needed
        }
        
        # Initialize Google Translate client if API key is provided
        if google_api_key:
            try:
                self.google_client = translate.Client(api_key=google_api_key)
                logger.info("Google Translate client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Translate client: {str(e)}")
        
        # Initialize DeepL client if API key is provided
        if deepl_api_key:
            try:
                self.deepl_client = deepl.Translator(deepl_api_key)
                logger.info("DeepL client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize DeepL client: {str(e)}")
        
        # Check if at least one translation service is available
        if not self.google_client and not self.deepl_client:
            logger.warning("No translation services are available. Translation functionality will be limited.")
    
    def detect_language(self, text):
        """
        Detect the language of the input text.
        
        Args:
            text (str): Text to detect language for.
            
        Returns:
            str: ISO language code (e.g., 'en').
        """
        if not text or not text.strip():
            return 'en'  # Default to English for empty text
        
        try:
            # Try to use Google Translate for detection if available
            if self.google_client:
                result = self.google_client.detect_language(text)
                return result['language']
            
            # Fallback to langdetect
            return detect(text)
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return 'en'  # Default to English on failure
    
    def translate(self, text, source_lang='auto', target_lang='en'):
        """
        Translate text using available translation services.
        
        Args:
            text (str): Text to translate.
            source_lang (str): Source language code (or 'auto' for detection).
            target_lang (str): Target language code.
            
        Returns:
            str: Translated text.
        """
        if not text or not text.strip():
            return text
            
        if source_lang == 'auto':
            source_lang = self.detect_language(text)
            
        # No need to translate if source and target are the same
        if source_lang == target_lang:
            return text
            
        # Try DeepL first if available (generally higher quality)
        if self.deepl_client:
            try:
                deepl_source = None if source_lang == 'auto' else self.language_mapping.get(source_lang, {}).get('deepl')
                deepl_target = self.language_mapping.get(target_lang, {}).get('deepl')
                
                if deepl_target:
                    result = self.deepl_client.translate_text(
                        text,
                        source_lang=deepl_source,
                        target_lang=deepl_target
                    )
                    return result.text
            except Exception as e:
                logger.warning(f"DeepL translation failed: {str(e)}")
                # Fall through to Google Translate
        
        # Try Google Translate if available
        if self.google_client:
            try:
                result = self.google_client.translate(
                    text,
                    target_language=target_lang,
                    source_language=None if source_lang == 'auto' else source_lang
                )
                return result['translatedText']
            except Exception as e:
                logger.error(f"Google translation failed: {str(e)}")
        
        # If all translation services fail, return original text
        logger.warning("All translation services failed. Returning original text.")
        return text
    
    def get_supported_languages(self):
        """
        Get a list of supported language codes.
        
        Returns:
            list: List of supported language codes.
        """
        return list(self.language_mapping.keys())