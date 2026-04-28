# Apple-Inspired PDF Tools Web Application

A beautiful, sleek, and high-performance minimalist web application to manipulate PDF documents. Inspired by the clean aesthetics of Apple and tools like iLovePDF, this application is built with Python, Flask, and Vanilla HTML/CSS.

## Features Included

1. **Merge PDF:** Combine multiple PDF files into one.
2. **Split PDF:** Separate a PDF into individual pages or split by ranges.
3. **Extract Pages:** Pull specific pages from a document.
4. **Protect PDF:** Add password encryption to a PDF.
5. **PDF to Images:** Convert a PDF document into a ZIP of high-quality images.
6. **Images to PDF:** Combine multiple images (JPG/PNG) into a single PDF document.
7. **PDF to Word:** Convert a PDF into an editable `.docx` file.
8. **Word to PDF:** Convert a Word document (`.docx`) into a standard PDF.
9. **Flatten PDF:** Renders pages as images, making text unselectable.
10. **OCR PDF:** Scans a flattened PDF and adds a text layer making it searchable.

## Architecture

This app uses a modular structure with **Flask Blueprints**. Every feature has its own file inside the `features/` directory.

- `app.py`: The main entry point.
- `features/`: The backend logic for each tool.
- `templates/`: HTML structures.
- `static/`: CSS and JS for the Apple-like UI and Progress Bars.

## Setup & Installation

1. Ensure you have Python 3.8+ installed.
2. Navigate to the directory:
   ```bash
   cd d:\pdf-tools
   ```
3. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

### Important Dependencies Note
- **Word to PDF (`docx2pdf`):** This library requires Microsoft Word to be installed on the machine running this application.
- **OCR PDF (`pytesseract` / `pdf2image`):** This feature requires two system-level packages to be installed on your machine:
  1. **Tesseract-OCR:** You must install the Tesseract executable and ensure it is in your system PATH.
  2. **Poppler:** Required to extract images from the PDF before passing them to Tesseract.
  
*(Note: If Tesseract is not installed, the application will still run perfectly. The OCR tool will simply inform the user gracefully that it requires installation).*

## Running the App

To start the server, simply run:
```bash
python app.py
```
Then, open your browser and navigate to `http://127.0.0.1:5000/`.
