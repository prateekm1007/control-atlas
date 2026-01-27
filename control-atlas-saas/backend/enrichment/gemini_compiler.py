import google.generativeai as genai
import os, json
class GeminiCompiler:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDqYHXLcT5xTkxh0LytevllKOsDv_jJKMA")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
    def synthesize(self, verdict, score, gen, results):
        prompt = f"Structural Biologist: Analyze {verdict} for {gen}. Results: {json.dumps(results)}. Write 2-sentence rationale."
        try: return self.model.generate_content(prompt).text.replace('*','')
        except: return "Causal reasoning layer offline."
gemini = GeminiCompiler()
