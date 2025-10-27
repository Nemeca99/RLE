# Data Tools for Magic Square Candidate Management

## Features
- **Compress**: Convert plain `.txt` base36 logs to `.lz4` for massive space savings.
- **Decode & Index**: Convert `.lz4` logs to Parquet or SQLite for fast querying, scoring, and visualization.
- **Batch/Stream Processing**: Handles millions of candidates efficiently, in chunks.

## Usage

### 1. Compress a .txt file to .lz4
```
python decode_and_index_candidates.py --txt near_magic_candidates.txt --lz4 near_magic_candidates.lz4 --compress
```

### 2. Decode and index to Parquet
```
python decode_and_index_candidates.py --lz4 near_magic_candidates.lz4 --to-parquet near_magic_candidates.parquet --decode-parquet
```

### 3. Decode and index to SQLite
```
python decode_and_index_candidates.py --lz4 near_magic_candidates.lz4 --to-sqlite near_magic_candidates.sqlite --decode-sqlite
```

## Querying and Visualization
- Use `pandas.read_parquet()` or `sqlite-utils`/`sqlite3` to filter, score, and visualize candidates.
- Use `grid_base36_utils.base36_to_grid()` to convert any base36 string back to a 3x3 grid for display or re-testing.

## Requirements
- Python 3.8+
- lz4, pandas, pyarrow, sqlite-utils

## Example: Visualize Top Candidates
```python
import pandas as pd
import grid_base36_utils

df = pd.read_parquet('near_magic_candidates.parquet')
top = df.nsmallest(10, 'delta')
for _, row in top.iterrows():
    print('Delta:', row['delta'])
    print(grid_base36_utils.base36_to_grid(row['base36']))
```

---
This workflow enables research-grade, scalable, and reproducible analysis of millions of near-magic square candidates.
