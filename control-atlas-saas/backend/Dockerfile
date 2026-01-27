FROM python:3.11-bookworm
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    wget ca-certificates libgl1 libxrender1 libsm6 libxext6 \
 && rm -rf /var/lib/apt/lists/*

# ChimeraX AppImage (headless-safe)
RUN wget -O /usr/local/bin/chimerax \
    https://github.com/RBVI/ChimeraX/releases/download/v1.7/ChimeraX-1.7-Ubuntu20.04.AppImage \
 && chmod +x /usr/local/bin/chimerax

# Python deps
RUN pip install --no-cache-dir \
    fastapi uvicorn python-multipart fpdf2 biopython numpy google-generativeai

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
