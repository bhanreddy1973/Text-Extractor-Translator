"""
File handler utility for managing file uploads and downloads.
"""
import os
import uuid
import shutil
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """
    Utility for handling file uploads, downloads, and management.
    """
    
    def __init__(self, upload_folder, allowed_extensions=None):
        """
        Initialize the file handler.
        
        Args:
            upload_folder (str): Path to the folder where uploads will be stored
            allowed_extensions (set, optional): Set of allowed file extensions
        """
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions or {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'tiff', 'bmp'}
        
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def allowed_file(self, filename):
        """
        Check if the file extension is allowed.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            bool: True if the file extension is allowed, False otherwise
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_upload(self, file_obj):
        """
        Save an uploaded file to the upload folder.
        
        Args:
            file_obj: File object from request.files
            
        Returns:
            str: Path to the saved file
        """
        if file_obj and self.allowed_file(file_obj.filename):
            # Generate a unique filename to avoid collisions
            original_filename = secure_filename(file_obj.filename)
            filename = f"{uuid.uuid4()}_{original_filename}"
            file_path = os.path.join(self.upload_folder, filename)
            
            file_obj.save(file_path)
            logger.info(f"Saved uploaded file: {file_path}")
            
            return file_path
        else:
            logger.warning(f"Invalid file upload attempt: {file_obj.filename if file_obj else 'None'}")
            raise ValueError("Invalid file type")
    
    def save_result(self, result_data, original_filename, result_folder):
        """
        Save processing results to a file.
        
        Args:
            result_data (str): Result data to save
            original_filename (str): Original filename for reference
            result_folder (str): Folder to save results in
            
        Returns:
            str: Path to the saved result file
        """
        # Create result folder if it doesn't exist
        os.makedirs(result_folder, exist_ok=True)
        
        # Generate a unique filename for the result
        base_name = os.path.splitext(secure_filename(original_filename))[0]
        result_filename = f"{base_name}_result_{uuid.uuid4()}.txt"
        result_path = os.path.join(result_folder, result_filename)
        
        # Save the result
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(result_data)
            
        logger.info(f"Saved result file: {result_path}")
        
        return result_path
    
    def cleanup_old_files(self, folder_path, max_age_hours=24):
        """
        Clean up old files from a folder.
        
        Args:
            folder_path (str): Path to the folder to clean up
            max_age_hours (int): Maximum age of files in hours
        """
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # Skip if not a file
            if not os.path.isfile(file_path):
                continue
                
            # Check file age
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove old file {file_path}: {str(e)}")