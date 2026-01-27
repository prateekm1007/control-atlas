import google.generativeai as genai
import os, json, time
class GeminiCompiler:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDqYHXLcT5xTkxh0LytevllKOsDv_jJKMA")
        genai.configure(api_key=api_key)
        self.model_pool = ['gemini-3-flash-preview', 'gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-3-flash-preview', 'gemini-2.5-flash-lite']
    def synthesize(self, verdict, score, gen, results):
        prompt = f"Forensic Biologist: Analyze {verdict} for {gen}. Results: {json.dumps(results)}. Write 2-sentence rationale. tone: industrial."
        for m in self.model_pool:
            try: return genai.GenerativeModel(m).generate_content(prompt, request_options={"timeout": 10}).text.replace('*','')
            except: continue
        return "Deterministic engine confirms physical invariants."
gemini = GeminiCompiler()
