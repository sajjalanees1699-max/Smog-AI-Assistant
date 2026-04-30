# ============================================================
#  backend.py — PDF Text Extraction
#  This file reads the uploaded PDF and returns clean text
#  Library needed: pip install pdfplumber
# ============================================================

import pdfplumber
import re


def extract_text_from_pdf(uploaded_file):
    """
    Takes the Streamlit uploaded PDF file object.
    Returns clean extracted text as a single string.
    """
    full_text = ""

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page_number, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text += f"\n--- Page {page_number + 1} ---\n"
                    full_text += page_text

        # Basic cleaning — remove extra spaces and blank lines
        full_text = re.sub(r'\n\s*\n', '\n\n', full_text)  # remove extra blank lines
        full_text = re.sub(r' +', ' ', full_text)           # remove extra spaces

        return full_text.strip()

    except Exception as e:
        return f"ERROR: Could not read PDF. Details: {str(e)}"


def get_text_preview(text, max_chars=500):
    """
    Returns a short preview of extracted text.
    Useful for debugging — shows first 500 characters.
    """
    if text.startswith("ERROR"):
        return text
    return text[:max_chars] + "..." if len(text) > max_chars else text
