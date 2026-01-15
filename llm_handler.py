import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

class LLMHandler:
    def __init__(self):
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text