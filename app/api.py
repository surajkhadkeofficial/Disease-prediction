import os
from google import genai
from dotenv import load_dotenv

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

def setup_gemini_client():
    """Initializes the new Google GenAI client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        # Create a client using the new SDK
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"Gemini Connection Error: {e}")
        return None

# Initialize the client once when the app starts
client = setup_gemini_client()

def get_ai_analysis(symptoms, history, age, gender):
    """Sends patient data to Gemini and returns clinical assessment text."""
    if not client:
        return "Error: API Key missing or invalid. Please check your .env file."

    prompt = f"""
    Patient Profile: Age {age}, {gender}.
    Medical History: {history}
    Presenting Symptoms: "{symptoms}"

    Task: Provide a clinical assessment including:
    1. Provisional Diagnosis
    2. Differential Diagnosis
    3. Recommended Tests
    4. Treatment Plan
    """
    try:
        # Generate content using the new client syntax and the latest flash model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Error: {e}"