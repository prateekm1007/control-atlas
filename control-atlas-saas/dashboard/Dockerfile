FROM python:3.11-slim
WORKDIR /app
RUN pip install streamlit requests
COPY . .
CMD ["streamlit", "run", "dashboard.py", "--server.port", "8502", "--server.address", "0.0.0.0"]
