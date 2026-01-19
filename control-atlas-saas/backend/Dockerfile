FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc g++ gfortran libopenblas-dev liblapack-dev curl git libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
# Force clean install without cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p uploads results tools structures
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
