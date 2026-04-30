# ============================================================
#  ai_engine.py — Groq AI Integration
#  Groq is FREE, FAST, and very reliable
#  Library needed: pip install groq
# ============================================================

from groq import Groq
import json
import re

# ══════════════════════════════════════════════════════════════
#  👇 APNI GROQ API KEY YAHAN DAALO
#  Free key milegi: https://console.groq.com
#  Sign up → API Keys → Create Key → Copy → Paste here
# ══════════════════════════════════════════════════════════════
API_KEY = ""

# Groq model — free and very fast (updated 2025)
MODEL = "llama-3.3-70b-versatile"


def _get_client():
    """Returns configured Groq client."""
    return Groq(api_key=API_KEY)


# ══════════════════════════════════════════════════════════════
#  FUNCTION 1 — Test API Connection
# ══════════════════════════════════════════════════════════════
def test_api_connection():
    """Tests if Groq API key is working."""
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=5,
    )
    return True, f"✅ Groq Connected! Model: {MODEL}"


# ══════════════════════════════════════════════════════════════
#  FUNCTION 2 — Generate Summary
# ══════════════════════════════════════════════════════════════
def get_summary(text):
    """Returns a 3-sentence summary of the PDF text."""
    client = _get_client()
    text_chunk = text[:4000]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an environmental science expert. Be concise and professional."
            },
            {
                "role": "user",
                "content": f"""Read this air quality report and write a summary in exactly 3 sentences.
Focus on: location, key pollution findings, and main health concern.
Write only 3 sentences. No bullet points. No headings.

Text:
{text_chunk}"""
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


# ══════════════════════════════════════════════════════════════
#  FUNCTION 3 — Extract Pollutant Data
# ══════════════════════════════════════════════════════════════
def extract_pollutants(text):
    """
    Extracts pollutant values from text.
    Returns dict: {"PM2.5": 87.4, "PM10": 142.6, ...}
    """
    client = _get_client()
    text_chunk = text[:4000]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a data extraction expert. Return only valid JSON. No explanation."
            },
            {
                "role": "user",
                "content": f"""Extract pollutant concentration values from this text.
Return ONLY this JSON format, nothing else:
{{"PM2.5": 0.0, "PM10": 0.0, "NO2": 0.0, "SO2": 0.0, "CO": 0.0, "O3": 0.0}}

Rules:
- Numbers only (no units in the JSON values)
- If a pollutant is not found, use 0.0
- Return ONLY the JSON object, no other text

Text:
{text_chunk}"""
            }
        ],
        max_tokens=150,
    )

    raw = response.choices[0].message.content.strip()

    # Clean markdown if present
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()

    # Extract JSON object
    json_match = re.search(r'\{[^{}]+\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group()

    data = json.loads(raw)

    # Ensure all keys exist and are floats
    defaults = {"PM2.5": 0.0, "PM10": 0.0, "NO2": 0.0,
                "SO2": 0.0, "CO": 0.0, "O3": 0.0}
    for key in defaults:
        if key not in data:
            data[key] = 0.0
        else:
            data[key] = float(data[key])

    return data


# ══════════════════════════════════════════════════════════════
#  FUNCTION 4 — Generate Full Report
# ══════════════════════════════════════════════════════════════
def get_report(text):
    """Generates a 3-paragraph environmental health report."""
    client = _get_client()
    text_chunk = text[:4000]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a senior environmental health analyst. Write formal professional reports."
            },
            {
                "role": "user",
                "content": f"""Write a professional 3-paragraph environmental report based on this data:

Paragraph 1: Pollution levels and comparison to WHO guidelines.
Paragraph 2: Health risks for public and vulnerable groups.
Paragraph 3: Three specific recommendations to reduce pollution.

No headings. No bullet points. Just 3 clean paragraphs.

Text:
{text_chunk}"""
            }
        ],
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


# ══════════════════════════════════════════════════════════════
#  FUNCTION 5 — Calculate AQI from PM2.5
# ══════════════════════════════════════════════════════════════
def calculate_aqi(pm25_value):
    """Returns (aqi_number, label, color) based on PM2.5 value."""
    pm25_value = float(pm25_value)

    if pm25_value == 0.0:
        return (0,   "No Data",              "#718096")
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
