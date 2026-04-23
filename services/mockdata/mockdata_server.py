import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

HTTP_PORT = 8080
DATA_ID = os.getenv("DATA_ID", "test-id")

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

if __name__ == "__main__":
    httpd = HTTPServer(('0.0.0.0', HTTP_PORT), MockDataHandler)
    print(f"Mock data server started on port {HTTP_PORT}")
    httpd.serve_forever()
