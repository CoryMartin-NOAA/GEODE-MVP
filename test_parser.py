import pytest, json
from parser import decode_observation

def test_valid_observation_passes_qc():
    raw = json.dumps({"station_id": "X", "timestamp": "2026-04-22T12:00:00Z", "temperature_celsius": 15.5}).encode('utf-8')
    assert decode_observation(raw)["qc_flag"] == "PASS"

def test_extreme_temperature_fails_qc():
    raw = json.dumps({"station_id": "X", "timestamp": "2026-04-22T12:05:00Z", "temperature_celsius": 105.0}).encode('utf-8')
    assert decode_observation(raw)["qc_flag"] == "FAIL_GROSS_ERROR"

def test_missing_required_field_raises_error():
    with pytest.raises(KeyError):
        decode_observation(json.dumps({"timestamp": "2026-04-22T12:00:00Z"}).encode('utf-8'))
