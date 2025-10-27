# RLE: Recursive Load Efficiency Monitor

[![Repository](https://img.shields.io/badge/GitHub-Nemeca99%2FRLE-blue)](https://github.com/Nemeca99/RLE)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

**RLE** measures hardware efficiency by balancing useful output vs stress, waste, instability, and time-to-burnout. Real-time monitoring for GPU/CPU systems.

## 📁 Structure

```
RLE/
├── lab/           # 🧪 Main monitoring lab
│   ├── monitoring/      # Background daemons & tools
│   ├── analysis/        # Post-session analysis
│   ├── stress/          # Stress test generators
│   └── sessions/        # Session data (CSVs & screenshots)
├── Magic/         # 🔢 Separate project (magic squares)
└── README.md      # This file
```

## 🚀 Quick Start

### ⚡ One-Click Launch (Easiest)

**Just double-click `RUN_RLE.bat`** in the repo root!

It will automatically:
- ✅ Check Python installation
- ✅ Install dependencies
- ✅ Start the monitor
- ✅ Open live dashboard in browser
- ✅ Show where CSVs are being saved
- ✅ Generate auto-report when you stop monitoring

**When you stop monitoring** (Ctrl+C), you'll automatically get:
- 📄 Session summary report (`REPORT_rle_YYYYMMDD_HH.txt`)
- 🩺 Health verdict ("System healthy" / "Needs attention")
- 📊 Key metrics (temp, power, RLE, collapse rate)
- 💡 Personalized recommendations

### 🔧 Manual Start

```bash
# Option A: Full suite (monitor + live graphs)
cd lab
start_monitoring_suite.bat

# Option B: Monitoring only
cd lab
python start_monitor.py --mode gpu --sample-hz 1
```

### 📊 Analyze Session

```bash
# Quick analysis
python lab/analyze_session.py

# Validate system
python kia_validate.py
```

## 📊 RLE_real Formula

Computes a metric balancing useful output vs stress, waste, instability, and time-to-burnout:

```
RLE_real = (util × stability) / (A_load × (1 + 1/T_sustain))
```

Where:
- **util** = utilization percentage
- **stability** = 1 / (1 + util_stddev)
- **A_load** = current_power / rated_power
- **T_sustain** = time until thermal limit (seconds)

## 🎯 Features

### Improved Collapse Detection
- ✅ Rolling peak with decay (prevents false positives)
- ✅ Thermal evidence required (t_sustain < 60s OR temp > limit-5°C)
- ✅ Power evidence (A_load > 0.95)
- ✅ Hysteresis: 65% threshold for 7+ seconds
- ✅ Split diagnostics: E_th vs E_pw components

### Lab Tools

| Location | Purpose |
|----------|---------|
| `lab/monitoring/` | Background daemon for continuous logging |
| `lab/analysis/` | Post-session analysis & plotting tools |
| `lab/stress/` | CPU/GPU stress test generators |
| `lab/sessions/recent/` | Current gaming session CSVs |
| `lab/sessions/archive/` | Historical data & screenshots |

## 📊 CSV Output Format

Each session logs to `sessions/recent/rle_YYYYMMDD_HH.csv` with **15 columns** organized by type:
- **Identification**: `timestamp`, `device`
- **Efficiency Metrics**: `rle_smoothed`, `rle_raw`, `E_th`, `E_pw`, `rolling_peak`
- **Temperature Metrics**: `temp_c`, `vram_temp_c`, `t_sustain_s`
- **Power/Performance**: `power_w`, `util_pct`, `a_load`, `fan_pct`
- **Events/Diagnostics**: `collapse`, `alerts`

📚 **See `lab/docs/DATA_COLLECTION.md`** for complete data dictionary and interpretation guide.

Sample row:

| Column | Description | Example |
|--------|-------------|---------|
| `timestamp` | ISO UTC timestamp | `2025-10-27T12:34:56.789Z` |
| `device` | "gpu" or "cpu" | `gpu` |
| `rle_smoothed` | 5-sample rolling average RLE | `0.723456` |
| `rle_raw` | Instantaneous RLE | `0.845678` |
| `E_th` | Thermal efficiency component | `0.580000` |
| `E_pw` | Power efficiency component | `1.350000` |
| `temp_c` | Core temperature (°C) | `75.00` |
| `vram_temp_c` | VRAM/junction temp (°C) | `82.00` |
| `power_w` | Power draw (W) | `198.50` |
| `util_pct` | GPU utilization (%) | `99.00` |
| `a_load` | Normalized load (power/rated) | `0.993` |
| `t_sustain_s` | Seconds to thermal limit | `310.0` |
| `fan_pct` | Fan speed (%) | `80` |
| `rolling_peak` | Adaptive peak reference | `1.001545` |
| `collapse` | Collapse event flag (0/1) | `1` |
| `alerts` | Pipe-separated warnings | `GPU_TEMP_LIMIT\|VRAM_TEMP_LIMIT` |

## 📈 Example Session

From a typical gaming session:
```
Session: 26.6 minutes, 1597 samples
├─ Power: 15-200W range (median 184W)
├─ Temperature: 58-76°C (peak 76°C)
├─ Max RLE: 1.00
├─ Mean RLE: 0.17 (bimodal: idle vs maxed)
└─ Collapse Events: ~5% with improved detector (v0.3+)
```

**Interpretation**:
- System healthy (temp < 80°C)
- Hitting power limit frequently (at 200W rated)
- Bimodal load normal for gaming (idle menus + maxed gameplay)
- Low mean RLE from scene switching, not thermal issues

## 🔧 Magic Squares (Separate Project)

The `Magic/` folder contains magic square search code (intensive CPU/GPU workload).

See `Magic/README_data_tools.md` for details.

---

**Documentation**:
- 🚀 [Getting Started](GETTING_STARTED.md) - 5-minute walkthrough
- ⚡ [Quick Reference](QUICK_REFERENCE.md) - Command cheat sheet & CSV guide
- 🐛 [Troubleshooting](lab/docs/TROUBLESHOOTING.md) - Common issues & solutions
- 📖 [What is RLE?](lab/docs/WHAT_IS_RLE.md) - Formula explained with examples
- 📊 [Interpreting Results](lab/docs/INTERPRETING_RESULTS.md) - Guide to analyzing sessions
- 🏗️ [Architecture](lab/docs/ARCHITECTURE.md) - System diagrams & state machines
- 🚀 [Quick Start](lab/USAGE.md) - How to use the suite
- 🔧 [Full Guide](lab/README.md) - Complete documentation
- 🤖 [Agent Instructions](AGENTS.md) - For AI assistants

**Analysis Tools**:
- `analyze_session.py` - Single session analysis with health assessment
- `scripts/batch_analyze.py` - Multi-session comparison

**Recent improvements** (v0.3.0):
- ✅ Improved collapse detection (rolling peak, evidence requirements, 7s hysteresis) 
- ✅ Reduced false positives from 51% → single digits
- ✅ Added Streamlit real-time dashboard
- ✅ Split diagnostics (E_th vs E_pw)

See [CHANGELOG.md](CHANGELOG.md) for full version history.

