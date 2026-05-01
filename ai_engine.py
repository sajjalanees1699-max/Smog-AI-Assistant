# ============================================================
#  ai_engine.py — Google Gemini AI Integration
#  This file connects to Gemini and runs 3 tasks:
#  1. Summarize the research paper
#  2. Extract pollutant data as JSON
#  3. Generate a full environmental report
#  Library needed: pip install google-generativeai
# ============================================================

import google.generativeai as genai
import json
import re


# ── STEP 1: Configure Gemini with your API key ──────────────
# Replace "YOUR_GEMINI_API_KEY_HERE" with your actual key
# Get your free key at: https://aistudio.google.com
API_KEY = "YOUR_GEMINI_API_KEY_HERE"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")   # free and fast model


# ══════════════════════════════════════════════════════════════
#  FUNCTION 1 — Generate Summary
#  Input : raw text from PDF
#  Output: 3-sentence summary string
# ══════════════════════════════════════════════════════════════
def get_summary(text):
    """
    Sends PDF text to Gemini and gets a clean 3-sentence summary.
    Returns a plain string.
    """
    # Only send first 4000 characters to stay within token limits
    text_chunk = text[:4000]

    prompt = f"""
You are an environmental science expert.
Read the following research paper or air quality report and write a clear,
professional summary in exactly 3 sentences.

Focus on:
- What the report is about (location, time period)
- Key pollution findings
- Main health or environmental concern

Text:
{text_chunk}

Write only the 3-sentence summary. No bullet points. No headings.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Summary could not be generated. Error: {str(e)}"


# ══════════════════════════════════════════════════════════════
#  FUNCTION 2 — Extract Pollutant Data
#  Input : raw text from PDF
#  Output: Python dictionary with pollutant values
# ══════════════════════════════════════════════════════════════
def extract_pollutants(text):
    """
    Asks Gemini to extract pollutant concentration values from the text.
    Returns a Python dictionary like:
    {"PM2.5": 87.4, "PM10": 142.6, "NO2": 54.2, "SO2": 18.7, "CO": 1200, "O3": 65.3}
    If a pollutant is not found, returns 0.0 for that pollutant.
    """
    text_chunk = text[:4000]

    prompt = f"""
You are an environmental data extraction expert.
Extract pollutant concentration values from the text below.

Return ONLY a valid JSON object — no explanation, no markdown, no extra text.
Use this exact format:
{{
    "PM2.5": 0.0,
    "PM10": 0.0,
    "NO2": 0.0,
    "SO2": 0.0,
    "CO": 0.0,
    "O3": 0.0
}}

Rules:
- Use numeric values only (floats or integers)
- If a pollutant is NOT mentioned in the text, use 0.0
- Units should be µg/m³ (convert if needed)
- Return ONLY the JSON, nothing else

Text:
{text_chunk}
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Clean up in case Gemini adds markdown code fences
        raw = re.sub(r"```json", "", raw)
        raw = re.sub(r"```", "", raw)
        raw = raw.strip()

        # Parse JSON string into Python dictionary
        data = json.loads(raw)

        # Make sure all 6 keys exist (fill missing ones with 0.0)
        expected_keys = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
        for key in expected_keys:
            if key not in data:
                data[key] = 0.0

        return data

    except json.JSONDecodeError:
        # If Gemini returns something that can't be parsed, return zeros
        return {"PM2.5": 0.0, "PM10": 0.0, "NO2": 0.0,
                "SO2": 0.0, "CO": 0.0, "O3": 0.0}
    except Exception as e:
        return {"PM2.5": 0.0, "PM10": 0.0, "NO2": 0.0,
                "SO2": 0.0, "CO": 0.0, "O3": 0.0}


# ══════════════════════════════════════════════════════════════
#  FUNCTION 3 — Generate Full Environmental Report
#  Input : raw text from PDF
#  Output: detailed AI-written report string
# ══════════════════════════════════════════════════════════════
def get_report(text):
    """
    Generates a detailed 3-paragraph environmental health report.
    Returns a plain string with the full report.
    """
    text_chunk = text[:4000]

    prompt = f"""
You are a senior environmental health analyst writing an official report.
Based on the research paper or air quality data below, write a professional
environmental analysis report with exactly 3 paragraphs:

Paragraph 1 — POLLUTION ANALYSIS:
Describe the pollution levels found, which pollutants are most critical,
and how they compare to WHO guidelines.

Paragraph 2 — HEALTH IMPACT:
Explain the health risks for the general public and vulnerable groups
(children, elderly, people with asthma).

Paragraph 3 — RECOMMENDATIONS:
Give 3 specific, actionable recommendations to reduce pollution
and protect public health.

Text:
{text_chunk}

Write only the 3 paragraphs. Use formal, professional language.
No bullet points. No headings. Just 3 clean paragraphs.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Report could not be generated. Error: {str(e)}"


# ══════════════════════════════════════════════════════════════
#  FUNCTION 4 — Calculate AQI from PM2.5
#  Input : PM2.5 value (float)
#  Output: AQI number and label string
# ══════════════════════════════════════════════════════════════
def calculate_aqi(pm25_value):
    """
    Calculates AQI category based on PM2.5 concentration.
    Returns a tuple: (aqi_number, label, color)
    """
    if pm25_value == 0.0:
        return (0, "No Data", "#718096")
    elif pm25_value <= 12.0:
        return (50,  "Good",                 "#27AE60")
    elif pm25_value <= 35.4:
        return (100, "Moderate",             "#F39C12")
    elif pm25_value <= 55.4:
        return (150, "Unhealthy for Groups", "#E67E22")
    elif pm25_value <= 150.4:
        return (187, "Unhealthy",            "#C0392B")
    elif pm25_value <= 250.4:
        return (250, "Very Unhealthy",       "#8E44AD")
    else:
        return (301, "Hazardous",            "#7B241C")
