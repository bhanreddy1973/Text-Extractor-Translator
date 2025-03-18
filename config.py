"""
Configuration settings for the Text Extractor and Translator application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-for-development')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    
    # File upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads/')
    RESULTS_FOLDER = os.environ.get('RESULTS_FOLDER', 'results/')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tiff', 'pdf', 'bmp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # OCR configuration
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD', 'tesseract')
    
    # ML model configuration
    ML_MODEL_PATH = os.environ.get('ML_MODEL_PATH', 'models/trained/text_enhancement.h5')
    USE_GPU = os.environ.get('USE_GPU', 'False') == 'True'
    
    # Translation services
    GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY', '')
    DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY', '')
    
    # Performance configuration
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '4'))
    PARALLEL_PROCESSING = os.environ.get('PARALLEL_PROCESSING', 'True') == 'True'
    CACHE_ENABLED = os.environ.get('CACHE_ENABLED', 'True') == 'True'
    
    # Supported languages (ISO 639-1 codes)
    SUPPORTED_LANGUAGES = [
        'auto', 'en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'ru', 'zh', 'ja',
        'ko', 'ar', 'hi', 'bn', 'pa', 'te', 'ta', 'ur', 'fa', 'tr', 'pl',
        'uk', 'vi', 'th', 'id'
    ]
    
    # NLP processing options
    ENABLE_SPELL_CHECK = os.environ.get('ENABLE_SPELL_CHECK', 'True') == 'True'
    ENABLE_NER = os.environ.get('ENABLE_NER', 'True') == 'True'
    ENABLE_POST_CORRECTION = os.environ.get('ENABLE_POST_CORRECTION', 'True') == 'True'