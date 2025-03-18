"""
NLP processing service for improving extracted text quality.
"""
import re
import logging
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)

class NLPProcessor:
    """
    Service for applying NLP techniques to improve extracted text quality.
    """
    
    def __init__(self, enable_spell_check=True, enable_ner=True):
        """
        Initialize the NLP processor.
        
        Args:
            enable_spell_check (bool): Whether to enable spell checking
            enable_ner (bool): Whether to enable named entity recognition
        """
        self.enable_spell_check = enable_spell_check
        self.enable_ner = enable_ner
        self.nlp = None
        
        # Common text patterns to fix
        self.patterns = [
            (r'(\d+)\.(\d+)', r'\1.\2'),  # Fix decimal numbers
            (r'(\w+)\s+,\s+(\w+)', r'\1, \2'),  # Fix comma spacing
            (r'(\w+)\s+\.\s+(\w+)', r'\1. \2'),  # Fix period spacing
            (r'\s{2,}', ' '),  # Remove extra spaces
            (r'([a-z])([A-Z])', r'\1 \2'),  # Fix missing space between sentences
        ]
        
        # Initialize spaCy if available
        if SPACY_AVAILABLE and (enable_spell_check or enable_ner):
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {str(e)}")
    
    def process_text(self, text):
        """
        Process text using NLP techniques.
        
        Args:
            text (str): The text to process
            
        Returns:
            str: Processed text
        """
        if not text or not text.strip():
            return text
            
        # Fix common patterns
        processed_text = self._fix_patterns(text)
        
        # Apply spaCy processing if available
        if self.nlp:
            try:
                processed_text = self._apply_spacy_processing(processed_text)
            except Exception as e:
                logger.warning(f"spaCy processing failed: {str(e)}")
        
        # Fix paragraphs and formatting
        processed_text = self._fix_paragraphs(processed_text)
        
        return processed_text
    
    def _fix_patterns(self, text):
        """
        Fix common text patterns using regular expressions.
        
        Args:
            text (str): The text to process
            
        Returns:
            str: Processed text
        """
        processed = text
        
        for pattern, replacement in self.patterns:
            processed = re.sub(pattern, replacement, processed)
            
        return processed
    
    def _apply_spacy_processing(self, text):
        """
        Apply spaCy NLP processing to the text.
        
        Args:
            text (str): The text to process
            
        Returns:
            str: Processed text
        """
        doc = self.nlp(text)
        
        # Named Entity Recognition
        if self.enable_ner:
            # Preserve proper capitalization for named entities
            for ent in doc.ents:
                # This is a simplified approach - in a real implementation,
                # you would need to handle text replacement more carefully
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC']:
                    text = text.replace(ent.text, self._ensure_proper_case(ent.text))
        
        # Spell checking would be implemented here in a real application
        # This is a placeholder for a more sophisticated implementation
        
        return text
    
    def _ensure_proper_case(self, text):
        """
        Ensure proper capitalization for named entities.
        
        Args:
            text (str): Entity text
            
        Returns:
            str: Properly capitalized text
        """
        # Simple implementation - capitalize first letter of each word
        return ' '.join(word.capitalize() for word in text.split())
    
    def _fix_paragraphs(self, text):
        """
        Fix paragraph structure and formatting.
        
        Args:
            text (str): The text to process
            
        Returns:
            str: Processed text with improved paragraph structure
        """
        # Fix line breaks
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)  # Single line breaks become spaces
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple line breaks become double
        
        # Fix bullet points
        text = re.sub(r'(?<=\n)[\s•-]*(?=•)', '', text)  # Clean up bullet points
        
        return text