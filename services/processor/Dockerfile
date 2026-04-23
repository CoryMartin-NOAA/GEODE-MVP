FROM ubuntu:24.04
RUN apt-get update && apt-get install -y python3.12 python3-pip && rm -rf /var/lib/apt/lists/*
RUN ln -sf python3.12 /usr/bin/python3
WORKDIR /app
COPY requirements.txt .
RUN python3.12 -m pip install --no-cache-dir -r requirements.txt
COPY services/processor/main.py main.py
COPY services/processor/__init__.py services/processor/
COPY services/__init__.py services/
CMD ["python3.12", "main.py"]
