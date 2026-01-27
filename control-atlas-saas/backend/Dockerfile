FROM python:3.11-bookworm
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 libxrender1 libsm6 libxext6 \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi uvicorn python-multipart fpdf2 biopython numpy google-generativeai pillow

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
