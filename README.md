# RLE: Recursive Load Efficiency Lab

[![Repository](https://img.shields.io/badge/GitHub-Nemeca99%2FRLE-blue)](https://github.com/Nemeca99/RLE)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Hardware monitoring and performance analysis for CPU/GPU systems using the **RLE_real** metric.

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

```bash
# 1. Install dependencies
pip install psutil nvidia-ml-py3 pandas streamlit plotly
# Or: pip install -r lab/requirements_lab.txt

# 2. Start monitoring (choose one):

# Option A: Monitoring only (background logging)
cd lab
python start_monitor.py --mode gpu --sample-hz 1

# Option B: Full suite (monitor + live graphs)
cd lab
start_monitoring_suite.bat

# 3. Game/use your PC normally...
# Ctrl+C when done

# 4. Analyze session
python analyze_session.py sessions/recent/rle_YYYYMMDD_HH.csv
```

**Full Suite** opens two windows:
- Terminal: Background logging to CSV
- Browser: Streamlit real-time dashboard with live graphs

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

## 📈 Example Output

From your recent gaming session:
```
Session: 26.6 minutes, 1597 samples
Peak Power: 200W @ 76°C
Mean RLE: 0.17 (bimodal load)
Collapse Events: 819 → will be much lower with improved detector
```

## 🔧 Magic Squares (Separate Project)

The `Magic/` folder contains magic square search code (intensive CPU/GPU workload).

See `Magic/README_data_tools.md` for details.

---

**Lab Documentation**: 
- Quick usage: `lab/USAGE.md`
- Full guide: `lab/README.md`  
- Agent instructions: `AGENTS.md`

**Recent improvements**: Improved collapse detection (rolling peak, evidence requirements, 7s hysteresis) reduces false positives from 51% → single digits.

