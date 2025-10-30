# Miner's Unified Laws - Reproduction Guide

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements_lab.txt
   ```

2. **Run full reproduction**:
   ```bash
   python lab/analysis/reproduce_full.py
   ```

3. **Generated outputs**:
   - `lab/sessions/archive/REPRODUCTION_RESULTS.json` - Summary metrics
   - `lab/sessions/archive/plots/reproduced_*.png` - All figures
   - `lab/sessions/archive/REPRODUCTION_LOG.txt` - Execution log

## Device-Specific Datasets

### Phone (Galaxy S24 Ultra)
- **File**: `lab/sessions/archive/mobile/phone_all_benchmarks.csv`
- **Samples**: 1,280 (45 minutes across multiple workloads)
- **Temperature**: 33°C → 44°C
- **Power**: ~10W (passive cooling)

### Laptop (ARM Windows, Snapdragon 7c)
- **Files**: 
  - `sessions/laptop/rle_20251030_19.csv` (431 samples)
  - `sessions/laptop/rle_20251030_20 - Copy.csv` (1,118 samples)
- **Temperature**: Not logged
- **Power**: ~49W (passive cooling, CPU-only)

### PC (Desktop, NVIDIA GPU + CPU)
- **Files**: 
  - `lab/sessions/recent/rle_20251027_09.csv`
  - `lab/sessions/recent/rle_20251028_08.csv`
- **Temperature**: Mid-60s°C
- **Power**: Variable

## Reproduced Metrics

All figures are regenerated from source CSVs. Key metrics:

- **Universal Scaling**: CV spread < 50% ✅
- **Thermal Paths**: r = -0.36 ✅
- **Probabilistic Containment**: Below P_k bounded ✅
- **Cross-Device RLE**: 0.15-1.28 range across platforms ✅

## Theory

See `lab/MINERS_UNIFIED_AXIOMS.pdf` for complete mathematical framework.

