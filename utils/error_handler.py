"""
Error handling utility for the application.
"""
import traceback
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def handle_error(error, is_api=False):
    """
    Handle application errors consistently.
    
    Args:
        error (Exception): The exception that occurred
        is_api (bool): Whether the error occurred in an API endpoint
        
    Returns:
        tuple: (error_response, status_code)
    """
    logger.error(f"Error: {str(error)}")
    logger.debug(traceback.format_exc())
    
    # Determine error type and appropriate response
    if isinstance(error, ValueError):
        message = str(error)
        status_code = 400
    elif isinstance(error, FileNotFoundError):
        message = "File not found"
        status_code = 404
    elif isinstance(error, PermissionError):
        message = "Permission denied"
        status_code = 403
    else:
        message = "An unexpected error occurred"
        status_code = 500
    
    # Create error response
    if is_api:
        return jsonify({
            'status': 'error',
            'message': message,
            'error_type': error.__class__.__name__
        }), status_code
    else:
        # For web interface, return a more user-friendly message
        return jsonify({
            'error': message
        }), status_code