import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from paho.mqtt import client as mqtt_client
import os

HTTP_PORT = 8080
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'wis2/notifications/test')
DATA_ID = os.getenv('DATA_ID', 'test-id')

class MockDataHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == f"/{DATA_ID}.json":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            obs_data = {
                "id": DATA_ID,
                "station_id": "STATION_001",
                "observation_time": "2023-10-27T10:00:00Z",
                "latitude": 50.0,
                "longitude": 10.0,
                "parameter_name": "temperature",
                "parameter_value": 22.5,
                "units": "Celsius"
            }
            self.wfile.write(json.dumps(obs_data).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_http_server():
    httpd = HTTPServer(('0.0.0.0', HTTP_PORT), MockDataHandler)
    print(f"Mock data server started on port {HTTP_PORT}")
    httpd.serve_forever()

def publish_notification():
    client = mqtt_client.Client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
    except Exception as e:
        print(f"Failed to connect to MQTT: {e}")
        return

    data_url = f"http://mockdata:{HTTP_PORT}/{DATA_ID}.json"
    notification = {
        "id": DATA_ID,
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [10.0, 50.0]
        },
        "properties": {
            "data_identifier": "test-data-123",
            "publication_datetime": "2023-10-27T10:00:00Z",
            "topic": MQTT_TOPIC
        },
        "links": [
            {
                "rel": "canonical",
                "type": "application/json",
                "href": data_url
            }
        ]
    }

    client.publish(MQTT_TOPIC, json.dumps(notification))
    client.disconnect()
    print(f"Published notification for {DATA_ID}")

if __name__ == '__main__':
    daemon = threading.Thread(target=run_http_server, daemon=True)
    daemon.start()
    time.sleep(2)
    publish_notification()
    time.sleep(30)
    print("Simulation finished")
