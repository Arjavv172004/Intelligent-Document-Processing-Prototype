#!/usr/bin/env python3
"""
Script to create sample documents for testing the IDP system
"""

from PIL import Image, ImageDraw, ImageFont
import os
import random
from datetime import datetime, timedelta

def create_sample_invoice(invoice_num, company_name, amount, date, output_path):
    """Create a sample invoice image"""
    # Create image
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        header_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
        body_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Colors
    blue = (37, 99, 235)
    dark_gray = (31, 41, 55)
    gray = (107, 114, 128)
    
    # Header
    draw.text((50, 50), "INVOICE", fill=blue, font=title_font)
    draw.text((50, 90), f"Invoice #: {invoice_num}", fill=dark_gray, font=header_font)
    draw.text((50, 120), f"Date: {date}", fill=dark_gray, font=body_font)
    
    # Company info
    draw.text((50, 200), f"Bill To: {company_name}", fill=dark_gray, font=header_font)
    draw.text((50, 230), "123 Business Street", fill=gray, font=body_font)
    draw.text((50, 250), "Sydney, NSW 2000", fill=gray, font=body_font)
    draw.text((50, 270), "Australia", fill=gray, font=body_font)
    
    # Invoice details
    y_pos = 350
    draw.text((50, y_pos), "Description", fill=dark_gray, font=header_font)
    draw.text((400, y_pos), "Amount", fill=dark_gray, font=header_font)
    
    # Line
    draw.line([(50, y_pos + 30), (750, y_pos + 30)], fill=gray, width=1)
    
    # Items
    items = [
        ("Professional Services", f"${amount:.2f}"),
        ("GST (10%)", f"${amount * 0.1:.2f}"),
    ]
    
    y_pos += 50
    for desc, amt in items:
        draw.text((50, y_pos), desc, fill=dark_gray, font=body_font)
        draw.text((400, y_pos), amt, fill=dark_gray, font=body_font)
        y_pos += 30
    
    # Total
    draw.line([(50, y_pos), (750, y_pos)], fill=gray, width=2)
    y_pos += 20
    total = amount * 1.1
    draw.text((50, y_pos), "TOTAL", fill=blue, font=header_font)
    draw.text((400, y_pos), f"${total:.2f}", fill=blue, font=header_font)
    
    # Footer
    draw.text((50, height - 100), "Thank you for your business!", fill=gray, font=body_font)
    draw.text((50, height - 80), "Payment due within 30 days", fill=gray, font=small_font)
    
    # Save image
    image.save(output_path, 'PNG')
    print(f"Created invoice: {output_path}")

def create_sample_receipt(receipt_num, store_name, amount, date, output_path):
    """Create a sample receipt image"""
    width, height = 400, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        header_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        body_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Colors
    green = (16, 185, 129)
    dark_gray = (31, 41, 55)
    gray = (107, 114, 128)
    
    # Header
    draw.text((50, 30), store_name, fill=green, font=title_font)
    draw.text((50, 60), f"Receipt #{receipt_num}", fill=dark_gray, font=header_font)
    draw.text((50, 85), f"Date: {date}", fill=dark_gray, font=body_font)
    
    # Items
    y_pos = 150
    items = [
        ("Coffee", f"${amount * 0.6:.2f}"),
        ("Sandwich", f"${amount * 0.4:.2f}"),
    ]
    
    for desc, amt in items:
        draw.text((50, y_pos), desc, fill=dark_gray, font=body_font)
        draw.text((300, y_pos), amt, fill=dark_gray, font=body_font)
        y_pos += 25
    
    # Total
    draw.line([(50, y_pos + 10), (350, y_pos + 10)], fill=gray, width=1)
    y_pos += 30
    draw.text((50, y_pos), "TOTAL", fill=green, font=header_font)
    draw.text((300, y_pos), f"${amount:.2f}", fill=green, font=header_font)
    
    # Footer
    draw.text((50, height - 80), "Thank you for visiting!", fill=gray, font=body_font)
    draw.text((50, height - 60), "Have a great day!", fill=gray, font=small_font)
    
    image.save(output_path, 'PNG')
    print(f"Created receipt: {output_path}")

def create_sample_form(form_type, company_name, date, output_path):
    """Create a sample form image"""
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        header_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
        body_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Colors
    blue = (37, 99, 235)
    dark_gray = (31, 41, 55)
    gray = (107, 114, 128)
    
    # Header
    draw.text((50, 50), f"{form_type} FORM", fill=blue, font=title_font)
    draw.text((50, 90), f"Date: {date}", fill=dark_gray, font=body_font)
    
    # Company info
    draw.text((50, 150), f"Company: {company_name}", fill=dark_gray, font=header_font)
    draw.text((50, 180), "Contact Information:", fill=dark_gray, font=body_font)
    draw.text((50, 210), "Name: John Smith", fill=gray, font=body_font)
    draw.text((50, 230), "Email: john@company.com", fill=gray, font=body_font)
    draw.text((50, 250), "Phone: +61 2 1234 5678", fill=gray, font=body_font)
    
    # Form fields
    y_pos = 320
    fields = [
        ("Project Name:", "Website Redesign"),
        ("Budget:", "$15,000"),
        ("Timeline:", "3 months"),
        ("Status:", "In Progress"),
    ]
    
    for field, value in fields:
        draw.text((50, y_pos), field, fill=dark_gray, font=body_font)
        draw.text((300, y_pos), value, fill=gray, font=body_font)
        y_pos += 30
    
    # Signature
    draw.text((50, height - 150), "Signature:", fill=dark_gray, font=body_font)
    draw.line([(200, height - 120), (400, height - 120)], fill=gray, width=1)
    draw.text((200, height - 100), "John Smith", fill=gray, font=small_font)
    
    image.save(output_path, 'PNG')
    print(f"Created form: {output_path}")

def main():
    """Create sample documents"""
    # Create sample_docs directory
    os.makedirs('static/sample_docs', exist_ok=True)
    
    # Sample data
    companies = [
        "ABC Traders Pty Ltd",
        "Sydney Tech Solutions",
        "Melbourne Business Co",
        "Perth Digital Services",
        "Brisbane Innovation Hub"
    ]
    
    # Create invoices
    for i in range(3):
        invoice_num = f"INV-2024-{1000 + i}"
        company = random.choice(companies)
        amount = random.uniform(500, 5000)
        date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%d/%m/%Y")
        create_sample_invoice(invoice_num, company, amount, date, f"static/sample_docs/invoice_{i+1}.png")
    
    # Create receipts
    for i in range(3):
        receipt_num = f"RCP-{1000 + i}"
        store = random.choice(["Coffee Corner", "Quick Mart", "City Cafe"])
        amount = random.uniform(10, 100)
        date = (datetime.now() - timedelta(days=random.randint(1, 7))).strftime("%d/%m/%Y")
        create_sample_receipt(receipt_num, store, amount, date, f"static/sample_docs/receipt_{i+1}.png")
    
    # Create forms
    form_types = ["Project Request", "Expense Report", "Timesheet"]
    for i, form_type in enumerate(form_types):
        company = random.choice(companies)
        date = (datetime.now() - timedelta(days=random.randint(1, 14))).strftime("%d/%m/%Y")
        create_sample_form(form_type, company, date, f"static/sample_docs/form_{i+1}.png")
    
    print("\nSample documents created successfully!")
    print("Files created in static/sample_docs/")

if __name__ == "__main__":
    main()
