FROM python:3.11-slim
WORKDIR /app
RUN pip install confluent-kafka pandas pyarrow s3fs paho-mqtt requests pytest flake8
COPY . .
CMD ["python", "ingest_worker.py"]
