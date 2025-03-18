"""
Main Flask application for Text Extractor and Translator.
"""
import os
import time
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename

from models.ocr_model import OCRModel
from models.translation_model import TranslationModel
from models.ml_enhancement import MLEnhancementModel
from services.image_preprocessing import ImagePreprocessor
from services.text_extraction import TextExtractionService
from services.translation_service import TranslationService
from utils.file_handler import FileHandler
from utils.error_handler import handle_error
from utils.performance_metrics import track_performance
import config

app = Flask(__name__)
app.config.from_object(config.Config)

# Initialize services
file_handler = FileHandler(app.config['UPLOAD_FOLDER'])
image_preprocessor = ImagePreprocessor()
ocr_model = OCRModel()
ml_model = MLEnhancementModel()
translation_model = TranslationModel()

text_extraction_service = TextExtractionService(
    ocr_model=ocr_model,
    ml_model=ml_model,
    preprocessor=image_preprocessor
)

translation_service = TranslationService(translation_model)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.route('/extract', methods=['POST'])
@track_performance
def extract_text():
    """Handle text extraction from uploaded file."""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Get parameters
        source_lang = request.form.get('source_lang', 'auto')
        enhance = request.form.get('enhance', 'true').lower() == 'true'
        
        # Save and process file
        start_time = time.time()
        file_path = file_handler.save_upload(file)
        
        # Extract text
        extracted_text, confidence = text_extraction_service.extract_text(
            file_path, 
            source_lang=source_lang,
            enhance=enhance
        )
        
        processing_time = time.time() - start_time
        
        # Return results
        return render_template(
            'results.html',
            text=extracted_text,
            confidence=confidence,
            processing_time=processing_time,
            filename=file.filename
        )
    
    except Exception as e:
        return handle_error(e)

@app.route('/translate', methods=['POST'])
@track_performance
def translate_text():
    """Handle text translation."""
    try:
        text = request.form.get('text', '')
        source_lang = request.form.get('source_lang', 'auto')
        target_lang = request.form.get('target_lang', 'en')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        # Translate text
        translated_text = translation_service.translate(
            text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        return jsonify({
            'original_text': text,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
    
    except Exception as e:
        return handle_error(e)

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """API endpoint for text extraction and optional translation."""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Get parameters
        source_lang = request.form.get('source_lang', 'auto')
        target_lang = request.form.get('target_lang', None)
        enhance = request.form.get('enhance', 'true').lower() == 'true'
        
        # Save and process file
        start_time = time.time()
        file_path = file_handler.save_upload(file)
        
        # Extract text
        extracted_text, confidence = text_extraction_service.extract_text(
            file_path, 
            source_lang=source_lang,
            enhance=enhance
        )
        
        # Translate if target language is specified
        translated_text = None
        if target_lang and target_lang != source_lang:
            translated_text = translation_service.translate(
                extracted_text,
                source_lang=source_lang,
                target_lang=target_lang
            )
        
        processing_time = time.time() - start_time
        
        # Return results
        response = {
            'status': 'success',
            'original_text': extracted_text,
            'confidence_score': confidence,
            'language_detected': source_lang if source_lang != 'auto' else translation_service.detect_language(extracted_text),
            'processing_time': f"{processing_time:.2f}s"
        }
        
        if translated_text:
            response['translated_text'] = translated_text
            response['target_language'] = target_lang
            
        return jsonify(response)
    
    except Exception as e:
        return handle_error(e, is_api=True)

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed results."""
    try:
        return send_file(
            os.path.join(app.config['RESULTS_FOLDER'], secure_filename(filename)),
            as_attachment=True
        )
    except Exception as e:
        return handle_error(e)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)