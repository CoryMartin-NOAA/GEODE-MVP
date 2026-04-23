import json

def decode_observation(payload_bytes):
    try:
        data = json.loads(payload_bytes.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON payload received.")

    for key in ["station_id", "timestamp", "temperature_celsius"]:
        if key not in data:
            raise KeyError(f"Missing required field: '{key}'")

    temp = data["temperature_celsius"]
    data["qc_flag"] = "PASS" if (-90.0 <= temp <= 60.0) else "FAIL_GROSS_ERROR"
    return data
