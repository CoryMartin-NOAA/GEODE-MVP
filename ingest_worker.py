import json, requests
import paho.mqtt.client as mqtt
from confluent_kafka import Producer

MQTT_BROKER = "globalbroker.meteo.fr"
MQTT_PORT = 8883
MQTT_TOPIC = "origin/a/wis2/+/data/core/weather/surface-based-observations/#"
KAFKA_BROKER = "redpanda:9092"
KAFKA_TOPIC = "raw-observations-incoming"

kafka_producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"🌍 Connected to WMO Global Broker at {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Failed to connect: {rc}")

def on_message(client, userdata, msg):
    try:
        wnm_payload = json.loads(msg.payload.decode('utf-8'))
        data_url = next((link.get("href") for link in wnm_payload.get("links", []) if link.get("rel") in ["canonical", "data"]), None)
        
        if not data_url: return
        print(f"🔗 Notification received! Fetching: {data_url}")

        response = requests.get(data_url, timeout=10)
        response.raise_for_status()
        
        kafka_message = {
            "wis2_metadata": wnm_payload.get("properties", {}),
            "source_url": data_url,
            "raw_payload_hex": response.content.hex()
        }
        kafka_producer.produce(KAFKA_TOPIC, key=wnm_payload.get("id", ""), value=json.dumps(kafka_message))
        kafka_producer.poll(0)
        print(f"✅ Fetched and published {len(response.content)} bytes.")

    except Exception as e:
        print(f"❌ Error processing message: {e}")

def main():
    print("🚀 Starting WIS 2.0 MQTT Ingest Gateway...")
    mqtt_client = mqtt.Client()
    mqtt_client.tls_set()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        pass
    finally:
        mqtt_client.disconnect()
        kafka_producer.flush()

if __name__ == '__main__':
    main()
