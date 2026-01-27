FROM python:3.11-bookworm
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn python-multipart fpdf2 biopython numpy google-generativeai
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
