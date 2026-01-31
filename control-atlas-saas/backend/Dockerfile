FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV PYTHONPATH=/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN touch __init__.py ingestion/__init__.py engine/__init__.py artifacts/__init__.py \
    glossary/__init__.py discovery/__init__.py generation/__init__.py enrichment/__init__.py router/__init__.py
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
