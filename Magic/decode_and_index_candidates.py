import lz4.frame
import pandas as pd
import sqlite3
import pyarrow as pa
import pyarrow.parquet as pq
import grid_base36_utils
import os

def decode_lz4_to_parquet(lz4_path, parquet_path, batch_size=100000):
    """
    Read a .lz4-compressed file of base36\tdelta lines, decode, and write to Parquet in batches.
    """
    records = []
    with lz4.frame.open(lz4_path, 'rt') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            if '\t' in line:
                base36, delta = line.split('\t')
                delta = float(delta)
            else:
                base36, delta = line, None
            grid = grid_base36_utils.base36_to_grid(base36)
            records.append({'base36': base36, 'delta': delta, 'grid': grid.flatten().tolist()})
    if records:
        df = pd.DataFrame(records)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_path)
    print(f"Decoded and indexed to {parquet_path}")

def decode_lz4_to_sqlite(lz4_path, sqlite_path, batch_size=100000):
    """
    Read a .lz4-compressed file of base36\tdelta lines, decode, and write to SQLite in batches.
    """
    conn = sqlite3.connect(sqlite_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        base36 TEXT PRIMARY KEY,
        delta REAL,
        grid TEXT
    )''')
    records = []
    with lz4.frame.open(lz4_path, 'rt') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            if '\t' in line:
                base36, delta = line.split('\t')
                delta = float(delta)
            else:
                base36, delta = line, None
            grid = grid_base36_utils.base36_to_grid(base36)
            grid_str = ','.join(str(x) for x in grid.flatten())
            records.append((base36, delta, grid_str))
            if len(records) >= batch_size:
                c.executemany('INSERT OR IGNORE INTO candidates VALUES (?, ?, ?)', records)
                conn.commit()
                records = []
        if records:
            c.executemany('INSERT OR IGNORE INTO candidates VALUES (?, ?, ?)', records)
            conn.commit()
    conn.close()
    print(f"Decoded and indexed to {sqlite_path}")

def compress_txt_to_lz4(txt_path, lz4_path):
    with open(txt_path, 'rb') as fin, lz4.frame.open(lz4_path, 'wb') as fout:
        fout.write(fin.read())
    print(f"Compressed {txt_path} to {lz4_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Decode, index, and compress base36 candidate files.")
    parser.add_argument('--txt', help='Input .txt file (base36[\tdelta])')
    parser.add_argument('--lz4', help='Input/output .lz4 file')
    parser.add_argument('--to-parquet', help='Output Parquet file')
    parser.add_argument('--to-sqlite', help='Output SQLite file')
    parser.add_argument('--compress', action='store_true', help='Compress .txt to .lz4')
    parser.add_argument('--decode-parquet', action='store_true', help='Decode .lz4 to Parquet')
    parser.add_argument('--decode-sqlite', action='store_true', help='Decode .lz4 to SQLite')
    args = parser.parse_args()

    if args.compress and args.txt and args.lz4:
        compress_txt_to_lz4(args.txt, args.lz4)
    if args.decode_parquet and args.lz4 and args.to_parquet:
        decode_lz4_to_parquet(args.lz4, args.to_parquet)
    if args.decode_sqlite and args.lz4 and args.to_sqlite:
        decode_lz4_to_sqlite(args.lz4, args.to_sqlite)
