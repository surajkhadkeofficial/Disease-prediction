import json
import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL_NAME

class AIService:
    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    def analyze(self, symptoms, history, age, gender):
        if not self.model:
            return {
                "provisional_diagnosis": "AI not configured",
                "differential_diagnosis": "Set GEMINI_API_KEY in .env",
                "recommended_tests": "N/A",
                "treatment_plan": "N/A",
                "medicine_suggestions": "N/A",
                "notes": "AI key is missing or invalid."
            }

        prompt = f"""
You are a medical report assistant. Return only valid JSON.

Patient details:
- Age: {age}
- Gender: {gender}
- Medical history: {history}
- Symptoms: {symptoms}

JSON format:
{{
  "provisional_diagnosis": "",
  "differential_diagnosis": "",
  "recommended_tests": "",
  "treatment_plan": "",
  "medicine_suggestions": "",
  "notes": ""
}}

Rules:
- Keep language simple and professional.
- Do not write extra text outside JSON.
- Medicine suggestions should be general and not prescription-only.
- Add a cautionary note that final decision must be made by a doctor.
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            data = json.loads(text)
            return data

        except Exception as e:
            return {
                "provisional_diagnosis": "Error",
                "differential_diagnosis": "Error",
                "recommended_tests": "Error",
                "treatment_plan": "Error",
                "medicine_suggestions": "Error",
                "notes": f"AI analysis failed: {e}"
            }