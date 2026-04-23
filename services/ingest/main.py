import os
import json
import logging
import httpx
import boto3
from paho.mqtt import client as mqtt_client
from confluent_kafka import Producer
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MQTT_BROKER = "globalbroker.meteo.fr"  # Change if your broker is elsewhere
MQTT_PORT = 443
MQTT_TOPIC = "origin/a/wis2/us-noaa-nws/data/core/weather/surface-based-observations"
MQTT_USERNAME = "everyone"
MQTT_PASSWORD = "everyone"

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:19092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'observations-raw')

S3_ENDPOINT = os.getenv('S3_ENDPOINT', 'http://localhost:9000')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', 'minioadmin')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', 'minioadmin')
S3_BUCKET = os.getenv('S3_BUCKET', 'observations')

# Initialize S3
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

# Ensure bucket exists
try:
    s3_client.create_bucket(Bucket=S3_BUCKET)
except Exception as e:
    logger.info(f"Bucket might already exist: {e}")

# Initialize Kafka Producer
kafka_producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    logger.info(f"Received message from {msg.topic}")
    try:
        notification = json.loads(msg.payload.decode())
        process_notification(notification)
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def process_notification(notification):
    # WIS2 Notification is GeoJSON
    # Links usually contain the canonical URL
    links = notification.get('links', [])
    canonical_url = next((link['href'] for link in links if link.get('rel') == 'canonical'), None)

    if not canonical_url:
        logger.warning("No canonical link found in notification")
        return

    logger.info(f"Downloading data from {canonical_url}")
    try:
        response = httpx.get(canonical_url)
        response.raise_for_status()
        data = response.content

        # Save to MinIO
        file_id = notification.get('id', 'unknown')
        s3_key = f"raw/{file_id}"
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=data)
        logger.info(f"Saved to S3: {s3_key}")

        # Publish to Kafka
        kafka_msg = {
            'notification': notification,
            's3_key': s3_key,
            's3_bucket': S3_BUCKET
        }
        kafka_producer.produce(
            KAFKA_TOPIC,
            key=file_id,
            value=json.dumps(kafka_msg).encode('utf-8')
        )
        kafka_producer.flush()
        logger.info("Published to Kafka")

    except Exception as e:
        logger.error(f"Failed to process notification: {e}")

def run():
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set()  # Enable TLS
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_forever()

if __name__ == '__main__':
    run()
