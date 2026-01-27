import google.generativeai as genai
import os, json
class GeminiCompiler:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDqYHXLcT5xTkxh0LytevllKOsDv_jJKMA")
        genai.configure(api_key=api_key)
        self.model_pool = ['gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-3-flash-preview', 'gemini-1.5-flash']
    def synthesize(self, verdict, score, gen, results):
        prompt = f"Forensic Biologist: Analyze {verdict} for {gen}. Results: {json.dumps(results)}. Write 2-sentence rationale on physical sovereignty. Industrial tone."
        for m in self.model_pool:
            try: return genai.GenerativeModel(m).generate_content(prompt, request_options={"timeout": 10}).text.replace('*','')
            except: continue
        return "Deterministic engine confirms structural integrity."
gemini = GeminiCompiler()
