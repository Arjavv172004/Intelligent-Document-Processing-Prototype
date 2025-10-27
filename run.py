#!/usr/bin/env python3
"""
Startup script for the Innovo IDP application
"""

import os
import sys
import subprocess
import platform

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check if Tesseract is installed
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Tesseract OCR detected")
        else:
            print("⚠️  Tesseract OCR not found - some features may not work")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Tesseract OCR not found - some features may not work")
    
    return True

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ['uploads', 'static/sample_docs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_sample_documents():
    """Create sample documents if they don't exist"""
    print("📄 Creating sample documents...")
    
    sample_docs_dir = 'static/sample_docs'
    if not os.listdir(sample_docs_dir):
        try:
            subprocess.run([sys.executable, 'create_sample_docs.py'], check=True)
            print("✅ Sample documents created")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to create sample documents")
    else:
        print("✅ Sample documents already exist")

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Innovo IDP application...")
    print("\n" + "="*60)
    print("🎯 INNOVO INTELLIGENT DOCUMENT PROCESSOR")
    print("="*60)
    print("📱 Main Interface: http://localhost:5001")
    print("📊 Analytics Dashboard: http://localhost:5001/dashboard")
    print("🛑 Press Ctrl+C to stop the application")
    print("="*60 + "\n")
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def main():
    """Main startup function"""
    print("🎯 Innovo Intelligent Document Processor")
    print("🚀 Initializing application...\n")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create sample documents
    create_sample_documents()
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
