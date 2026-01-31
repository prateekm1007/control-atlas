FROM python:3.11-slim

# Install system dependencies for PDF and BioPython
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ensure PYTHONPATH is baked into the image
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from the backend folder into /app
COPY . /app

# Ensure all __init__.py files exist
RUN touch __init__.py api/__init__.py artifacts/__init__.py engine/__init__.py \
    enrichment/__init__.py glossary/__init__.py discovery/__init__.py generation/__init__.py

EXPOSE 8000

# Run uvicorn from the root /app to ensure absolute imports work
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
