# ============================================================
#  ai_engine.py — Groq AI Integration (Llama 3)
#  This file connects to Groq and runs 3 tasks:
#  1. Summarize the research paper
#  2. Extract pollutant data as JSON
#  3. Generate a full environmental report
#  Library needed: pip install groq
# ============================================================

import os
from groq import Groq
import json
import re

# ── STEP 1: Configure Groq with your API key ──────────────
# Replace "YOUR_GROQ_API_KEY_HERE" with your actual key
# Or better: set it as an environment variable
API_KEY = "apikey"

client = Groq(api_key=API_KEY)
MODEL_NAME = "llama-3.3-70b-versatile"  # Groq's high-performance model


# ══════════════════════════════════════════════════════════════
#  FUNCTION 1 — Generate Summary
# ══════════════════════════════════════════════════════════════
def get_summary(text):
    """
    Sends PDF text to Groq and gets a clean 3-sentence summary.
    """
    text_chunk = text[:4000]

    prompt = f"""
    You are an environmental science expert.
    Read the following research paper or air quality report and write a clear,
    professional summary in exactly 3 sentences.
    Focus on: location, pollution findings, and health concerns.

    Text:
    {text_chunk}

    Write only the 3-sentence summary. No bullet points. No headings.
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary could not be generated. Error: {str(e)}"


# ══════════════════════════════════════════════════════════════
#  FUNCTION 2 — Extract Pollutant Data
# ══════════════════════════════════════════════════════════════
def extract_pollutants(text):
    """
    Asks Groq to extract pollutant concentration values as JSON.
    """
    text_chunk = text[:4000]

    prompt = f"""
    Extract pollutant concentration values from the text below.
    Return ONLY a valid JSON object using this exact format:
    {{
        "PM2.5": 0.0,
        "PM10": 0.0,
        "NO2": 0.0,
        "SO2": 0.0,
        "CO": 0.0,
        "O3": 0.0
    }}
    Rules: Numeric values only, use 0.0 if not mentioned.

    Text:
    {text_chunk}
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
            response_format={"type": "json_object"} # Ensures valid JSON
        )
        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)

        # Fill missing keys if any
        expected_keys = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
        for key in expected_keys:
            if key not in data:
                data[key] = 0.0

        return data

    except Exception:
        return {"PM2.5": 0.0, "PM10": 0.0, "NO2": 0.0, "SO2": 0.0, "CO": 0.0, "O3": 0.0}


# ══════════════════════════════════════════════════════════════
#  FUNCTION 3 — Generate Full Environmental Report
# ══════════════════════════════════════════════════════════════
def get_report(text):
    """
    Generates a detailed 3-paragraph environmental health report.
    """
    text_chunk = text[:4000]

    prompt = f"""
    Write a professional 3-paragraph environmental analysis report based on the text.
    Paragraph 1: Pollution Analysis vs WHO guidelines.
    Paragraph 2: Health risks for vulnerable groups.
    Paragraph 3: 3 specific recommendations.

    Text:
    {text_chunk}

    Write only the 3 paragraphs. No headings.
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_NAME,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Report could not be generated. Error: {str(e)}"


# ══════════════════════════════════════════════════════════════
#  FUNCTION 4 — Calculate AQI (No Change Needed)
# ══════════════════════════════════════════════════════════════
def calculate_aqi(pm25_value):
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
