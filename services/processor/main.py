import os
import json
import logging
import uuid
from datetime import datetime, timezone
import boto3
import psycopg2
from pybufrkit.decoder import Decoder
from confluent_kafka import Consumer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:19092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'observations-raw')

S3_ENDPOINT = os.getenv('S3_ENDPOINT', 'http://localhost:9000')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', 'minioadmin')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', 'minioadmin')

DB_URL = os.getenv('DB_URL', 'postgresql://observations_user:observations_password@localhost:5432/observations_db')

# Initialize S3
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

def get_db_connection():
    return psycopg2.connect(DB_URL)

def setup_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id TEXT PRIMARY KEY,
            station_id TEXT,
            observation_time TIMESTAMP,
            latitude FLOAT,
            longitude FLOAT,
            parameter_name TEXT,
            parameter_value FLOAT,
            units TEXT,
            qc_status TEXT,
            raw_data_key TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def decode_bufr(data_bytes):
    decoder = Decoder()
    bufr_message = decoder.decode(data_bytes)
    # This is a very simplified BUFR extraction for demonstration
    # Real BUFR extraction depends heavily on the specific descriptors
    return {
        "id": str(uuid.uuid4()),
        "station_id": "BUFR_STN",
        "observation_time": datetime.now(timezone.utc).isoformat(),
        "latitude": 0.0,
        "longitude": 0.0,
        "parameter_name": "unknown",
        "parameter_value": 0.0,
        "units": "unknown"
    }

def decode_and_qc(data, is_bufr=False):
    if is_bufr:
        obs = decode_bufr(data)
    else:
        obs = json.loads(data.decode('utf-8') if isinstance(data, bytes) else data)

    # Basic Quality Control
    qc_status = 'PASSED'
    if obs.get('parameter_name') == 'temperature':
        if obs['parameter_value'] < -100 or obs['parameter_value'] > 60:
            qc_status = 'FAILED'

    return obs, qc_status

def process_message(msg_value):
    task = json.loads(msg_value)
    s3_bucket = task['s3_bucket']
    s3_key = task['s3_key']
    notification = task.get('notification', {})

    # Check if it's BUFR based on notification media type
    is_bufr = False
    links = notification.get('links', [])
    for link in links:
        if link.get('rel') == 'canonical' and 'bufr' in link.get('type', '').lower():
            is_bufr = True
            break

    logger.info(f"Processing data from S3: {s3_key} (is_bufr={is_bufr})")

    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    raw_data = response['Body'].read()

    observations, qc_status = decode_and_qc(raw_data, is_bufr=is_bufr)

    # Store in DB
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO observations (id, station_id, observation_time, latitude, longitude, parameter_name, parameter_value, units, qc_status, raw_data_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                qc_status = EXCLUDED.qc_status,
                parameter_value = EXCLUDED.parameter_value
        """, (
            observations['id'],
            observations['station_id'],
            observations['observation_time'],
            observations['latitude'],
            observations['longitude'],
            observations['parameter_name'],
            observations['parameter_value'],
            observations['units'],
            qc_status,
            s3_key
        ))
        conn.commit()
        logger.info(f"Stored observation {observations['id']} in DB with QC status {qc_status}")
    except Exception as e:
        logger.error(f"Failed to store in DB: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def run():
    setup_db()

    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'processor-group',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe([KAFKA_TOPIC])

    logger.info("Processor service started, consuming from Kafka...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka error: {msg.error()}")
                continue

            process_message(msg.value().decode('utf-8'))
    finally:
        consumer.close()

if __name__ == '__main__':
    run()
