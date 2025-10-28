# Proof: Sessions Evidence

## What This Document Is
Evidence index for sessions demonstrating RLE working on real workloads. Use this to locate CSVs, reports, and how to verify.

## Where to Look
- Current runs: `lab/sessions/recent/`
  - Hourly CSVs: `rle_YYYYMMDD_HH.csv`
  - Auto text reports: `REPORT_rle_*.txt`
  - Multi-page PDF: `rle_gaming_report.pdf`
- Historical: `lab/sessions/archive/`
  - Older CSVs and plots
  - Use `.gitkeep` placeholder if empty

## Key Recent Evidence
- Files (examples):
  - `recent/rle_20251028_08.csv` (36.1 min, 4320 samples)
  - `recent/rle_20251028_07.csv` (2 hours)
  - `recent/rle_20251028_06.csv`
  - `recent/rle_20251028_05.csv`
  - `recent/rle_20251028_04.csv`
- Reports:
  - `recent/REPORT_rle_20251028_08.txt` — summary stats and verdict
  - `recent/rle_gaming_report.pdf` — per-hour RLE/temp/power/collapse plots

## What the Evidence Shows
- CSV schema matches v0.3.0 (frozen) including `rle_smoothed`, `E_th`, `E_pw`, `rolling_peak`, `collapse`.
- Multi-hour gaming: ~29,930 combined samples; temps 39–80°C; 0% collapses in recent set.
- PDF plots: hour-by-hour RLE/Temp/Power timelines with collapse markers.

## How to Verify
- Quick summary (multi-file):
```
python lab/analysis/summarize_sessions.py \
  lab/sessions/recent/rle_20251028_08.csv \
  lab/sessions/recent/rle_20251028_07.csv \
  lab/sessions/recent/rle_20251028_06.csv \
  lab/sessions/recent/rle_20251028_05.csv \
  lab/sessions/recent/rle_20251028_04.csv
```
- Single session analysis:
```
python lab/analyze_session.py lab/sessions/recent/rle_20251028_08.csv
```
- Generate per-hour PDF (already generated):
```
python lab/analysis/report_sessions.py \
  lab/sessions/recent/rle_gaming_report.pdf \
  lab/sessions/recent/rle_20251028_08.csv \
  lab/sessions/recent/rle_20251028_07.csv \
  lab/sessions/recent/rle_20251028_06.csv \
  lab/sessions/recent/rle_20251028_05.csv \
  lab/sessions/recent/rle_20251028_04.csv
```

## Baseline Example
- `lab/sessions/example_baseline_session.csv` — small, annotated example row set for tooling checks.

## Archival Practice
- Move old `recent/rle_*.csv` into `archive/` to keep recent clean.
- Name plots: `plots/rle_timeline_YYYYMMDD_HH.png` (optional convention).

## Cross-References
- RLE overview: `lab/docs/RLE_Master.md`
- Data schema details: `lab/docs/DATA_COLLECTION.md`
- Interpreting results: `lab/docs/INTERPRETING_RESULTS.md`
- Troubleshooting: `lab/docs/TROUBLESHOOTING.md`
