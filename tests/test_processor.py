import json
from services.processor.main import decode_and_qc

def test_decode_and_qc_passed():
    obs_data = {
        "id": "test-1",
        "station_id": "STN1",
        "observation_time": "2023-10-27T10:00:00Z",
        "latitude": 50.0,
        "longitude": 10.0,
        "parameter_name": "temperature",
        "parameter_value": 22.5,
        "units": "Celsius"
    }
    obs, qc_status = decode_and_qc(json.dumps(obs_data))
    assert obs["id"] == "test-1"
    assert qc_status == "PASSED"

def test_decode_and_qc_failed():
    obs_data = {
        "id": "test-2",
        "station_id": "STN1",
        "observation_time": "2023-10-27T10:00:00Z",
        "latitude": 50.0,
        "longitude": 10.0,
        "parameter_name": "temperature",
        "parameter_value": 122.5,
        "units": "Celsius"
    }
    obs, qc_status = decode_and_qc(json.dumps(obs_data))
    assert qc_status == "FAILED"

if __name__ == "__main__":
    test_decode_and_qc_passed()
    test_decode_and_qc_failed()
    print("All tests passed!")
