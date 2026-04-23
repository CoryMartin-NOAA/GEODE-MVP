FROM python:3.12-slim
WORKDIR /app
COPY mockdata_server.py .
COPY notify_and_serve.py .
RUN pip install paho-mqtt
EXPOSE 8080
CMD ["python", "notify_and_serve.py"]