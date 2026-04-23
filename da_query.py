import duckdb, time
print("🧪 Starting DA Data Extraction...")
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("CREATE SECRET minio_secret (TYPE s3, KEY_ID 'admin', SECRET 'password123', ENDPOINT 'localhost:9000', URL_STYLE 'path', USE_SSL false);")
try:
    df = con.execute("SELECT * FROM read_parquet('s3://earth-sys-obs/surface/*.parquet')").df()
    print(df.head())
except Exception as e:
    print("No data in MinIO yet! Generate some first.")
