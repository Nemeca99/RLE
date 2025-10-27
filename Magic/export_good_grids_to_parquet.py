import sqlite3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

DB = 'near_magic_candidates_streamable.sqlite'
GOOD_TABLE = 'good_grids'
PARQUET_OUT = 'good_grids.parquet'

# Connect and load all good grids
def export_to_parquet():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(f'SELECT * FROM {GOOD_TABLE}', conn)
    conn.close()
    table = pa.Table.from_pandas(df)
    pq.write_table(table, PARQUET_OUT)
    print(f"Exported {len(df)} good grids to {PARQUET_OUT}")

if __name__ == '__main__':
    export_to_parquet()
