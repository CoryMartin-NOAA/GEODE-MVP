FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/api/main.py main.py
COPY services/api/__init__.py services/api/
COPY services/__init__.py services/
CMD ["python", "main.py"]
