# 🌍 Earth System Observation Pipeline (Local Prototype)

This repository contains the local prototype for our modern Earth system observation ingest, quality control, and storage pipeline. It uses Docker Compose to simulate a cloud environment locally.

## Architecture
* **Message Broker:** Redpanda (Kafka compatible)
* **Storage:** MinIO (S3 compatible)
* **Database:** PostgreSQL + PostGIS (for STAC metadata)
* **Processing:** Python Ingest & Storage Workers

## 🚀 Quick Start Guide
1. Ensure Docker is running.
2. Run: `docker-compose up --build -d`
3. View MinIO at `http://localhost:9001` (admin / password123)
4. Run DA queries: `python da_query.py`
