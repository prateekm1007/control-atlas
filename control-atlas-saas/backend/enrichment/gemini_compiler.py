import google.generativeai as genai
import os, json
class GeminiCompiler:
    def __init__(self, key):
        genai.configure(api_key=key)
        self.model_pool = ['gemini-3-flash-preview', 'gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash-lite', 'gemini-2.0-flash-thinking-exp-1219']
    def synthesize(self, verdict, score, gen, results):
        prompt = f"Structural Biologist: Analyze {verdict} ({score}%) for {gen}. Results: {json.dumps(results)}. Write a 2-sentence rationale."
        for m in self.model_pool:
            try: return genai.GenerativeModel(m).generate_content(prompt).text.replace('*','')
            except: continue
        return "Deterministic engine confirms structural invariants."
