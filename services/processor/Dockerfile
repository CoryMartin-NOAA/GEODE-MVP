FROM python:3.12-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/processor/main.py main.py
COPY services/processor/__init__.py services/processor/
COPY services/__init__.py services/
CMD ["python", "main.py"]
