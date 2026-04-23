FROM python:3.12-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/ingest/main.py main.py
COPY services/ingest/__init__.py services/ingest/
COPY services/__init__.py services/
CMD ["python", "main.py"]
