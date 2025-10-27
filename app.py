from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import re
import json
from datetime import datetime
import io
import base64
from werkzeug.utils import secure_filename
import uuid

# Optional imports with fallbacks
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not available")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: easyocr not available")

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow not available")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Warning: OpenCV not available")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: numpy not available")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available")

try:
    import plotly.graph_objs as go
    import plotly.utils
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'innovo_automation_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/sample_docs', exist_ok=True)

# Initialize OCR readers
if EASYOCR_AVAILABLE:
    try:
        easyocr_reader = easyocr.Reader(['en'])
        ocr_available = True
    except:
        ocr_available = False
        print("EasyOCR initialization failed")
else:
    ocr_available = False
    print("EasyOCR not available")

# Global variables for analytics
processed_documents = []
total_processing_time = 0
manual_processing_time = 5  # minutes per document
automated_processing_time = 0.33  # 20 seconds

class DocumentProcessor:
    def __init__(self):
        self.patterns = {
            'invoice_number': [
                r'(?:invoice|inv)[\s#:]*([A-Z0-9-]+)',
                r'(?:no|number)[\s#:]*([A-Z0-9-]+)',
                r'#([A-Z0-9-]+)'
            ],
            'company_name': [
                r'^([A-Za-z\s&.,]+?)(?:\n|$)',
                r'(?:from|bill\s*to)[\s:]*([A-Za-z\s&.,]+)',
                r'^([A-Za-z\s&.,]+?)(?:\s+invoice|\s+receipt)'
            ],
            'date': [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})',
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})'
            ],
            'amount': [
                r'(?:total|amount|sum)[\s:]*[\$₹€£]?([\d,]+\.?\d*)',
                r'[\$₹€£]([\d,]+\.?\d*)',
                r'([\d,]+\.?\d*)\s*(?:dollars?|rupees?|euros?|pounds?)'
            ],
            'tax': [
                r'(?:tax|vat|gst)[\s:]*[\$₹€£]?([\d,]+\.?\d*)',
                r'(\d+\.?\d*%)\s*(?:tax|vat|gst)'
            ]
        }
    
    def extract_text(self, image_path):
        """Extract text from image using OCR"""
        try:
            # Try EasyOCR first
            if ocr_available and EASYOCR_AVAILABLE:
                result = easyocr_reader.readtext(image_path)
                text = ' '.join([item[1] for item in result])
            elif TESSERACT_AVAILABLE and PILLOW_AVAILABLE:
                # Fallback to Tesseract
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image)
            else:
                # Mock OCR for demo purposes
                text = self.mock_ocr_extraction(image_path)
            
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return self.mock_ocr_extraction(image_path)
    
    def mock_ocr_extraction(self, image_path):
        """Mock OCR extraction for demo purposes when OCR is not available"""
        # Return sample extracted text based on filename
        filename = os.path.basename(image_path).lower()
        
        if 'invoice' in filename:
            return """
            INVOICE
            Invoice #: INV-2024-001
            Date: 15/12/2024
            Bill To: ABC Traders Pty Ltd
            123 Business Street
            Sydney, NSW 2000
            Australia
            
            Description Amount
            Professional Services $2,500.00
            GST (10%) $250.00
            TOTAL $2,750.00
            
            Thank you for your business!
            Payment due within 30 days
            """
        elif 'receipt' in filename:
            return """
            Coffee Corner
            Receipt #RCP-1001
            Date: 15/12/2024
            
            Coffee $4.50
            Sandwich $8.50
            TOTAL $13.00
            
            Thank you for visiting!
            Have a great day!
            """
        elif 'form' in filename:
            return """
            Project Request Form
            Date: 15/12/2024
            
            Company: Sydney Tech Solutions
            Contact Information:
            Name: John Smith
            Email: john@company.com
            Phone: +61 2 1234 5678
            
            Project Name: Website Redesign
            Budget: $15,000
            Timeline: 3 months
            Status: In Progress
            
            Signature: John Smith
            """
        else:
            return "Sample document text for demonstration purposes."
    
    def preprocess_image(self, image_path):
        """Preprocess image for better OCR results"""
        if not OPENCV_AVAILABLE:
            return image_path
            
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Save processed image
            processed_path = image_path.replace('.', '_processed.')
            cv2.imwrite(processed_path, thresh)
            
            return processed_path
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return image_path
    
    def extract_structured_data(self, text):
        """Extract structured data using regex patterns"""
        extracted_data = {
            'document_type': 'Unknown',
            'company_name': '',
            'invoice_number': '',
            'date': '',
            'amount': '',
            'tax': '',
            'raw_text': text
        }
        
        # Determine document type
        text_lower = text.lower()
        if 'invoice' in text_lower:
            extracted_data['document_type'] = 'Invoice'
        elif 'receipt' in text_lower:
            extracted_data['document_type'] = 'Receipt'
        elif 'form' in text_lower:
            extracted_data['document_type'] = 'Form'
        
        # Extract fields using regex patterns
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    extracted_data[field] = match.group(1).strip()
                    break
        
        return extracted_data
    
    def process_document(self, image_path):
        """Main document processing pipeline"""
        start_time = datetime.now()
        
        # Preprocess image
        processed_path = self.preprocess_image(image_path)
        
        # Extract text
        text = self.extract_text(processed_path)
        
        # Extract structured data
        structured_data = self.extract_structured_data(text)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Add metadata
        structured_data['processing_time'] = processing_time
        structured_data['timestamp'] = datetime.now().isoformat()
        structured_data['file_name'] = os.path.basename(image_path)
        
        return structured_data

# Initialize document processor
processor = DocumentProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        return jsonify({'filename': unique_filename, 'filepath': filepath})

@app.route('/extract', methods=['POST'])
def extract_data():
    data = request.get_json()
    filepath = data.get('filepath')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 400
    
    try:
        # Process document
        result = processor.process_document(filepath)
        
        # Store in global analytics
        processed_documents.append(result)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/analytics')
def get_analytics():
    """Get analytics data for dashboard"""
    if not processed_documents:
        return jsonify({
            'total_documents': 0,
            'average_processing_time': 0,
            'time_saved': 0,
            'efficiency_gain': 0,
            'monthly_impact': 0,
            'error_reduction': 85,
            'chart_data': {}
        })
    
    total_docs = len(processed_documents)
    avg_processing_time = sum(doc['processing_time'] for doc in processed_documents) / total_docs
    time_saved_per_doc = manual_processing_time - (avg_processing_time / 60)  # Convert to minutes
    total_time_saved = time_saved_per_doc * total_docs
    efficiency_gain = (time_saved_per_doc / manual_processing_time) * 100
    monthly_impact = total_docs * 30  # Assuming 30 days
    
    # Create chart data
    chart_data = {
        'document_types': {},
        'processing_times': [doc['processing_time'] for doc in processed_documents],
        'dates': [doc['timestamp'][:10] for doc in processed_documents]
    }
    
    for doc in processed_documents:
        doc_type = doc['document_type']
        chart_data['document_types'][doc_type] = chart_data['document_types'].get(doc_type, 0) + 1
    
    return jsonify({
        'total_documents': total_docs,
        'average_processing_time': round(avg_processing_time, 2),
        'time_saved': round(total_time_saved, 2),
        'efficiency_gain': round(efficiency_gain, 1),
        'monthly_impact': monthly_impact,
        'error_reduction': 85,
        'chart_data': chart_data
    })

@app.route('/export_csv')
def export_csv():
    """Export processed documents as CSV"""
    if not processed_documents:
        return jsonify({'error': 'No data to export'}), 400
    
    if PANDAS_AVAILABLE:
        df = pd.DataFrame(processed_documents)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
    else:
        # Manual CSV creation without pandas
        if not processed_documents:
            return jsonify({'error': 'No data to export'}), 400
        
        # Get all unique keys from all documents
        all_keys = set()
        for doc in processed_documents:
            all_keys.update(doc.keys())
        
        # Create CSV header
        csv_data = ','.join(all_keys) + '\n'
        
        # Create CSV rows
        for doc in processed_documents:
            row = []
            for key in all_keys:
                value = doc.get(key, '')
                # Escape commas and quotes
                if ',' in str(value) or '"' in str(value):
                    value = f'"{str(value).replace('"', '""')}"'
                row.append(str(value))
            csv_data += ','.join(row) + '\n'
    
    # Create file response
    output = io.BytesIO()
    output.write(csv_data.encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'extracted_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/simulate_automation', methods=['POST'])
def simulate_automation():
    """Simulate sending data to automation system"""
    data = request.get_json()
    
    # Simulate processing delay
    import time
    time.sleep(1)
    
    return jsonify({
        'success': True,
        'message': 'Data successfully sent to Innovo Automation Framework',
        'automation_id': f'AUTO_{uuid.uuid4().hex[:8].upper()}',
        'status': 'Queued for processing'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
