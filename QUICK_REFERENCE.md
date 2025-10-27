# RLE Monitoring Lab - Quick Reference

## 🚀 Quick Commands

### Start Monitoring
```bash
# Full suite (monitor + dashboard)
start_monitoring_suite.bat

# Just the monitor
python start_monitor.py --mode gpu

# With custom settings
python start_monitor.py --mode gpu --sample-hz 2 --gpu-temp-limit 80
```

### Analyze Session
```bash
# Analyze latest session
python analyze_session.py

# Analyze specific session
python analyze_session.py sessions/recent/rle_20251027_04.csv

# Batch analysis
python scripts/batch_analyze.py sessions/recent/
```

### Validate System
```bash
# Validate RLE formula
python kia_validate.py sessions/recent/rle_20251027_04.csv
```

---

## 📊 CSV Columns Reference

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `timestamp` | ISO UTC | When sample was taken | `2025-10-27T04:33:22.489Z` |
| `device` | string | "gpu" or "cpu" | `gpu` |
| `rle_smoothed` | float | 5-sample rolling average | `0.723456` |
| `rle_raw` | float | Instantaneous RLE | `0.845678` |
| `E_th` | float | Thermal efficiency component | `0.580000` |
| `E_pw` | float | Power efficiency component | `1.350000` |
| `temp_c` | float | Core temperature (°C) | `75.00` |
| `vram_temp_c` | float | VRAM/junction temp (°C) | `82.00` |
| `power_w` | float | Power draw (W) | `198.50` |
| `util_pct` | float | GPU utilization (%) | `99.00` |
| `a_load` | float | Normalized load (power/rated) | `0.993` |
| `t_sustain_s` | float | Seconds to thermal limit | `310.0` |
| `fan_pct` | int | Fan speed (%) | `80` |
| `rolling_peak` | float | Adaptive peak reference | `1.001545` |
| `collapse` | int | Collapse event flag (0/1) | `1` |
| `alerts` | string | Pipe-separated warnings | `GPU_TEMP\|VRAM_TEMP` |

---

## 🧮 RLE Formula

```python
stability = 1 / (1 + stddev(util_last_5_samples))
T_sustain = (temp_limit - T_current) / max(dT/dt, ε)
denominator = a_load × (1 + 1/T_sustain)
RLE = (util × stability) / denominator

# Split components
E_th = stability / (1 + 1/T_sustain)  # Thermal efficiency
E_pw = util / a_load                   # Power efficiency
```

---

## ⚠️ Collapse Detection Logic

Triggered when ALL conditions met:
1. **Time**: At least 60s warmup elapsed
2. **Gate**: `util > 60%` OR `a_load > 0.75` AND `temp rising > 0.05°C/s`
3. **Drop**: `rle_smoothed < 0.65 × rolling_peak`
4. **Duration**: Sustained for 7+ consecutive seconds
5. **Evidence**: `t_sustain < 60s` OR `temp > (limit-5°C)` OR `a_load > 0.95`

---

## 📈 Interpreting RLE Values

| RLE Range | Interpretation | Action |
|-----------|----------------|--------|
| > 0.8 | Excellent efficiency | System running optimally |
| 0.5 - 0.8 | Good efficiency | Normal operation |
| 0.2 - 0.5 | Moderate efficiency | Check for thermal/power limits |
| < 0.2 | Poor efficiency | System may be overstressed |

---

## 🔍 Common Issues

### High Collapse Rate (>50%)
- **Cause**: Old detector (pre-v0.3) or truly overstressed system
- **Fix**: Check if using old CSV. New detector reduces false positives to <5%

### No Collapses
- **Cause**: System not under heavy load OR detector too strict
- **Fix**: Review temp/power logs. Collapse should be rare (<5%)

### Missing Columns (E_th, E_pw)
- **Cause**: CSV from old monitor (pre-v0.3)
- **Fix**: Re-record session with updated `hardware_monitor.py`

### High False Positive Rate
- **Cause**: Using simple 70% threshold (old detector)
- **Fix**: Use v0.3.0+ with rolling peak, evidence, hysteresis

---

## 🛠️ Troubleshooting

### Monitor not starting
```bash
# Check NVML
python -c "import pynvml; pynvml.nvmlInit()"

# Check dependencies
pip install -r requirements_lab.txt
```

### Streamlit dashboard not showing
- Check CSV path in `rle_streamlit.py`
- Verify monitor is writing to `sessions/recent/`
- Check browser console for errors

### CSV missing data
- Ensure monitor ran for >60 seconds
- Check for permission errors in `sessions/recent/`
- Verify NVML/psutil permissions

---

## 📁 Directory Structure

```
RLE/
├── lab/
│   ├── monitoring/        # Background daemons
│   │   ├── hardware_monitor.py  # Main daemon
│   │   └── rle_streamlit.py     # Dashboard
│   ├── analysis/          # Post-session tools
│   ├── stress/            # Load generators
│   ├── sessions/
│   │   ├── recent/        # Current CSVs
│   │   └── archive/        # Old data
│   └── docs/              # Documentation
├── Kia.yaml              # Agent config
├── kia_validate.py        # Validation script
└── QUICK_REFERENCE.md    # This file
```

---

## 🎯 Typical Workflow

1. **Start monitoring** → `start_monitoring_suite.bat`
2. **Play game / run workload** → Monitor generates CSV
3. **Analyze session** → `python analyze_session.py`
4. **Validate** → `python kia_validate.py`
5. **Check health** → Review collapse rate and temps
6. **Archive if needed** → Move CSV to `sessions/archive/`

---

## 📞 Key Files

- `AGENTS.md` - Full agent instructions for AI assistants
- `lab/README.md` - Lab documentation
- `lab/USAGE.md` - Usage guide
- `lab/docs/WHAT_IS_RLE.md` - Formula explained
- `lab/docs/INTERPRETING_RESULTS.md` - Analysis guide
- `lab/docs/ARCHITECTURE.md` - System diagrams
- `CHANGELOG.md` - Version history

---

**Last Updated**: Session 2025-10-27  
**Agent**: Kia v1.0

