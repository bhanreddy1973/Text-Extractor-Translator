"""
Image preprocessing service for enhancing OCR accuracy.
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """
    Service for preprocessing images to improve OCR accuracy.
    """
    
    def __init__(self):
        """Initialize the image preprocessor."""
        pass
    
    def preprocess(self, image, enhance_level='auto'):
        """
        Preprocess an image to enhance OCR accuracy.
        
        Args:
            image: PIL Image or numpy array
            enhance_level (str): Level of enhancement ('auto', 'low', 'medium', 'high')
            
        Returns:
            PIL.Image: Preprocessed image
        """
        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
            
        # Convert to grayscale if color image
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_array
            
        # Determine enhancement level based on image quality
        if enhance_level == 'auto':
            enhance_level = self._determine_enhancement_level(gray)
            
        # Apply enhancements based on level
        if enhance_level == 'low':
            processed = self._apply_low_enhancement(gray)
        elif enhance_level == 'medium':
            processed = self._apply_medium_enhancement(gray)
        elif enhance_level == 'high':
            processed = self._apply_high_enhancement(gray)
        else:
            processed = gray
            
        # Convert back to PIL Image
        return Image.fromarray(processed)
    
    def _determine_enhancement_level(self, img):
        """
        Determine the appropriate enhancement level based on image quality.
        
        Args:
            img (numpy.ndarray): Grayscale image array
            
        Returns:
            str: Enhancement level ('low', 'medium', 'high')
        """
        # Calculate image quality metrics
        blur = cv2.Laplacian(img, cv2.CV_64F).var()
        contrast = img.std()
        
        # Determine enhancement level based on metrics
        if blur > 100 and contrast > 50:
            return 'low'  # Good quality image needs minimal enhancement
        elif blur > 50 and contrast > 30:
            return 'medium'  # Medium quality image
        else:
            return 'high'  # Poor quality image needs significant enhancement
    
    def _apply_low_enhancement(self, img):
        """
        Apply low level enhancements to the image.
        
        Args:
            img (numpy.ndarray): Grayscale image array
            
        Returns:
            numpy.ndarray: Enhanced image
        """
        # Simple contrast adjustment
        enhanced = cv2.convertScaleAbs(img, alpha=1.1, beta=0)
        
        # Slight noise reduction
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        return enhanced
    
    def _apply_medium_enhancement(self, img):
        """
        Apply medium level enhancements to the image.
        
        Args:
            img (numpy.ndarray): Grayscale image array
            
        Returns:
            numpy.ndarray: Enhanced image
        """
        # Stronger contrast adjustment
        enhanced = cv2.convertScaleAbs(img, alpha=1.3, beta=10)
        
        # Noise reduction
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Adaptive thresholding for better text/background separation
        enhanced = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return enhanced
    
    def _apply_high_enhancement(self, img):
        """
        Apply high level enhancements to the image.
        
        Args:
            img (numpy.ndarray): Grayscale image array
            
        Returns:
            numpy.ndarray: Enhanced image
        """
        # Denoise more aggressively
        denoised = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
        
        # Increase contrast significantly
        enhanced = cv2.convertScaleAbs(denoised, alpha=1.5, beta=30)
        
        # Sharpen the image
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        # Apply Otsu's thresholding
        _, enhanced = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return enhanced
    
    def deskew(self, image):
        """
        Deskew an image to straighten text lines.
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            PIL.Image: Deskewed image
        """
        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
            
        # Convert to grayscale if color image
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_array
            
        # Detect skew angle
        try:
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find all contours
            contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            angles = []
            for contour in contours:
                # Filter small contours
                if cv2.contourArea(contour) < 100:
                    continue
                    
                # Get rotated rectangle
                rect = cv2.minAreaRect(contour)
                angle = rect[2]
                
                # Normalize angle
                if angle < -45:
                    angle = 90 + angle
                    
                angles.append(angle)
                
            # Calculate median angle
            if angles:
                median_angle = np.median(angles)
            else:
                median_angle = 0
                
            # Rotate image
            (h, w) = img_array.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            rotated = cv2.warpAffine(img_array, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return Image.fromarray(rotated)
        except Exception as e:
            logger.warning(f"Deskewing failed: {str(e)}")
            return image