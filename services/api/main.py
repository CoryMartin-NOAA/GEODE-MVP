import os
import logging
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.getenv('DB_URL', 'postgresql://observations_user:observations_password@localhost:5432/observations_db')

app = FastAPI(title="Earth Observation API")

class Observation(BaseModel):
    id: str
    station_id: str
    observation_time: datetime
    latitude: float
    longitude: float
    parameter_name: str
    parameter_value: float
    units: str
    qc_status: str

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.get("/observations", response_model=List[Observation])
def get_observations(station_id: Optional[str] = None, parameter: Optional[str] = None):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT id, station_id, observation_time, latitude, longitude, parameter_name, parameter_value, units, qc_status FROM observations"
    params = []

    conditions = []
    if station_id:
        conditions.append("station_id = %s")
        params.append(station_id)
    if parameter:
        conditions.append("parameter_name = %s")
        params.append(parameter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, params)
    rows = cur.fetchall()

    results = []
    for row in rows:
        results.append(Observation(
            id=row[0],
            station_id=row[1],
            observation_time=row[2],
            latitude=row[3],
            longitude=row[4],
            parameter_name=row[5],
            parameter_value=row[6],
            units=row[7],
            qc_status=row[8]
        ))

    cur.close()
    conn.close()
    return results

@app.get("/observations/{obs_id}", response_model=Observation)
def get_observation(obs_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, station_id, observation_time, latitude, longitude, parameter_name, parameter_value, units, qc_status FROM observations WHERE id = %s", (obs_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Observation not found")

    return Observation(
        id=row[0],
        station_id=row[1],
        observation_time=row[2],
        latitude=row[3],
        longitude=row[4],
        parameter_name=row[5],
        parameter_value=row[6],
        units=row[7],
        qc_status=row[8]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
