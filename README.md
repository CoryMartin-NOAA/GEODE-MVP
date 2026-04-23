# Modern Earth System Observation Ingest System

## Overview
This system is a modern replacement for legacy meteorological observation data ingest, quality control (QC), and storage. It supports:
- WIS2 notifications over MQTT.
- S3-compatible storage (MinIO) for raw data.
- Kafka-compatible messaging (Redpanda) for asynchronous processing.
- PostgreSQL/PostGIS for structured observation storage.
- FastAPI for data querying.
- Support for JSON and BUFR data formats.

## Architecture
1. **Mosquitto**: MQTT broker for WIS2 notifications.
2. **MinIO**: Object storage for raw data files.
3. **Redpanda**: Streaming platform for orchestrating processing tasks.
4. **PostgreSQL**: Relational database for storing decoded observations.
5. **Ingest Service**: Listens to MQTT, downloads data, stores in MinIO, and notifies the processor via Redpanda.
6. **Processor Service**: Consumes from Redpanda, decodes data (JSON/BUFR), performs QC, and stores in PostgreSQL.
7. **Query API**: Provides REST endpoints to retrieve observations.

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the System
1. Start the infrastructure and services:
   ```bash
   docker compose up -d
   ```
2. The services will be available at:
   - API: http://localhost:8000
   - MinIO Console: http://localhost:9001
   - Redpanda Console: http://localhost:18082

### Simulating Data Ingest
You can use the provided simulation script to trigger the ingest process:
```bash
python scripts/simulate_ingest.py
```

## Testing
Run unit tests with pytest:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```

## License
This project is part of NOAA-EMC Ecosystem. 

See LICENSE and DISCLAIMER for details.

## DISCLAIMER
This code is provided on an "as is" basis, and the user assumes responsibility for its use.
