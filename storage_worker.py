import json, time
import pandas as pd
import s3fs
from confluent_kafka import Consumer

S3_ENDPOINT = 'http://minio:9000'
BUCKET_NAME = 'earth-sys-obs'

def main():
    print("🚀 Starting Storage Worker...")
    fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': S3_ENDPOINT}, key='admin', secret='password123')
    if not fs.exists(BUCKET_NAME): fs.mkdir(BUCKET_NAME)

    consumer = Consumer({'bootstrap.servers': 'redpanda:9092', 'group.id': 'parquet-writer', 'auto.offset.reset': 'earliest'})
    consumer.subscribe(['raw-observations-incoming'])
    batch = []
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                if batch:
                    print(f"📦 Writing {len(batch)} records to Parquet...")
                    df = pd.DataFrame(batch)
                    df.to_parquet(f"s3://{BUCKET_NAME}/surface/batch_{int(time.time())}.parquet", engine='pyarrow', storage_options={"client_kwargs": {'endpoint_url': S3_ENDPOINT}, "key": "admin", "secret": "password123"})
                    batch = []
                continue
            if msg.error(): continue
            
            # Temporary placeholder logic until we integrate ecCodes for BUFR decoding
            obs = json.loads(msg.value().decode('utf-8'))
            print(f"📥 Received raw payload from {obs.get('source_url')}")
            # batch.append(...) -> We will populate this once we decode the BUFR hex!

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
