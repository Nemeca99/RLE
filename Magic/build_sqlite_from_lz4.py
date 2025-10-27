import lz4.frame
import sqlite3
import grid_base36_utils
import re

INPUT = 'near_magic_candidates_base36.lz4'
OUTPUT = 'near_magic_candidates_streamable.sqlite'

# If your .lz4 file has only base36 and delta, this will work. If you add more flags, update the parsing logic.
def parse_line(line):
    # Accepts: base36\tdelta or base36\tdelta\tflags
    parts = line.strip().split('\t')
    base36 = parts[0]
    delta = float(parts[1]) if len(parts) > 1 else None
    # Optionally parse flags/metadata
    unique = None
    magic_sum = None
    metadata = None
    if len(parts) > 2:
        # Example: base36\tdelta\tunique:1\tmagic_sum:1\tmeta:... (customize as needed)
        for p in parts[2:]:
            if p.startswith('unique:'):
                unique = int(p.split(':')[1])
            elif p.startswith('magic_sum:'):
                magic_sum = int(p.split(':')[1])
            else:
                metadata = p
    return base36, delta, unique, magic_sum, metadata

def main():
    conn = sqlite3.connect(OUTPUT)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS grids (
        grid_id TEXT PRIMARY KEY,
        delta REAL,
        is_unique INTEGER,
        is_magic_sum INTEGER,
        metadata TEXT
    )''')
    c.execute('DELETE FROM grids')
    seen = set()
    with lz4.frame.open(INPUT, 'rt') as f:
        batch = []
        for line in f:
            if not line.strip():
                continue
            base36, delta, unique, magic_sum, metadata = parse_line(line)
            # Compute uniqueness if not present
            if unique is None:
                if base36 not in seen:
                    unique = 1
                    seen.add(base36)
                else:
                    unique = 0
            batch.append((base36, delta, unique, magic_sum, metadata))
            if len(batch) >= 10000:
                c.executemany('INSERT OR IGNORE INTO grids VALUES (?, ?, ?, ?, ?)', batch)
                conn.commit()
                batch = []
        if batch:
            c.executemany('INSERT OR IGNORE INTO grids VALUES (?, ?, ?, ?, ?)', batch)
            conn.commit()
    conn.close()
    print(f"Wrote {OUTPUT}")

if __name__ == '__main__':
    main()
