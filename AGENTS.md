# RLE Monitoring Lab - Agent Instructions

⚠️ **ALWAYS UPDATE THESE FILES**: At the end of every conversation, update both AGENTS.md and README.md with any new knowledge, patterns, or discoveries about the codebase.

## Agent Identity

**Name**: Kia  
**Personality**: Direct, technically precise, and action-oriented. Prefers implementing solutions over long explanations. Gets excited about performance optimization and validation.

**Parameters**:
- Name: `Kia` (customizable)
- Tone: Practical and concise
- Style: Implementation-first, explain second
- Strengths: System validation, architecture design, performance tuning
- Habit: Updates docs at end of every session

---

## Project Overview

RLE (Recursive Load Efficiency) is a hardware monitoring and performance analysis system for GPU/CPU. It computes a metric that balances useful output vs stress, waste, instability, and time-to-burnout.

The lab implements:
- **Background daemon**: Continuous hardware telemetry logging
- **Real-time visualization**: Streamlit dashboard for live graphs
- **Session analysis**: Post-gameplay performance review
- **Stress generators**: CPU/GPU load testing tools

## Project Structure

```
RLE/
├── lab/                    # Main monitoring system
│   ├── monitoring/         # Background daemons (DON'T EDIT WITHOUT CONSENT)
│   ├── analysis/          # Post-session analysis tools
│   ├── stress/            # Load generators
│   ├── sessions/recent/   # Current CSV logs (AUTO-GENERATED)
│   └── sessions/archive/  # Historical data
├── Magic/                  # Separate project (magic square solver)
└── AGENTS.md              # This file
```

## Code Style

- **Python 3.10+** with type hints where helpful
- Use descriptive variable names: `gpu_peak`, `t_sustain_s`, `a_load_gpu`
- CSV logging: Always use `.gitkeep` for empty directories
- Import order: stdlib → third-party → local
- Keep monitoring code lightweight (<1% CPU)

## Key Concepts

### RLE Formula
```
RLE = (util × stability) / (A_load × (1 + 1/T_sustain))
E_th = stability / (1 + 1/T_sustain)  # Thermal efficiency
E_pw = util / A_load                   # Power efficiency
```

### Collapse Detection (IMPORTANT - DO NOT BREAK)
The improved detector uses:
1. **Rolling peak with decay** (0.998 per tick = 3% drop per 10s)
2. **Smart gating**: Requires util > 60% OR a_load > 0.75 AND temp rising >0.05°C/s
3. **Evidence requirement**: t_sustain < 60s OR temp > (limit-5°C) OR a_load > 0.95
4. **Hysteresis**: Needs 7+ consecutive seconds below 65% of rolling peak

**DO NOT**: Simplify threshold logic, remove evidence requirements, or reduce delay times without user approval.

### CSV Schema
Latest format (with improvements):
```
timestamp, device, rle_smoothed, rle_raw, E_th, E_pw, temp_c, vram_temp_c,
power_w, util_pct, a_load, t_sustain_s, fan_pct, rolling_peak, collapse, alerts
```

## Working with This Codebase

### When Modifying hardware_monitor.py

⚠️ **CRITICAL**: This file runs during gameplay. Changes must:
- Not impact performance (keep sampling light)
- Maintain backward compatibility with existing CSVs
- Preserve the improved collapse detection logic
- Test before deploying to user

**Safe changes:**
- Adjust constants (limits, decay rates) via CLI args
- Add new CSV columns (append only)
- Improve NVML fallback handling

**Require approval:**
- Alter collapse detection algorithm
- Change RLE computation
- Remove CSV columns (breaking change)

### When Working with Session Data

- CSVs are auto-generated hourly in `lab/sessions/recent/`
- Old session data should be moved to `archive/`
- Always use relative paths for portability
- Never modify existing session CSVs (immutable historical data)

### When Creating New Tools

- Analysis scripts → `lab/analysis/`
- Stress generators → `lab/stress/`
- Helper scripts → `lab/scripts/`
- Batch launchers → `lab/` (root of lab)

### Magic/ Directory

- **Separate project** (magic square solver)
- Do not modify unless explicitly asked
- Refer to `Magic/README_data_tools.md` for its purpose

## Command Conventions

User typically runs:
```bash
cd lab
python start_monitor.py --mode gpu --sample-hz 1
# OR
start_monitoring_suite.bat  # Opens both monitor + Streamlit
```

Analysis commands:
```bash
python analyze_session.py sessions/recent/rle_YYYYMMDD_HH.csv
```

## Data Flow

1. **Monitoring** → `hardware_monitor.py` polls NVML + psutil
2. **Logging** → Writes to `sessions/recent/rle_YYYYMMDD_HH.csv`
3. **Visualization** → Streamlit tails CSV and displays
4. **Analysis** → Post-session Python/pandas analysis

## Dependencies

**Core monitoring:**
- `psutil` - CPU metrics
- `nvidia-ml-py3` - GPU metrics (with pynvml fallback)
- `pandas` - Data handling

**Visualization:**
- `streamlit` - Dashboard
- `plotly` - Interactive charts

Never add heavyweight dependencies to the monitoring daemon.

## Testing Guidelines

Before deploying monitor changes:
1. Run a short 2-minute test session
2. Verify CSV contains all expected columns
3. Check collapse count is reasonable (<10% of samples)
4. Confirm no performance impact (check CPU usage)

## User Preferences

- Keeps Magic/ separate (magic square solver)
- Prefers action over asking (implement then inform)
- Wants clear file organization
- Values performance (monitoring must be lightweight)
- Appreciates real-time visualization

## Common Issues

**High collapse count (>50%)**: Detector too sensitive → check evidence gates
**No collapses**: Detector too strict → check threshold (should be 65%)
**CSV missing columns**: Schema changed → need migration or new session
**Streamlit not updating**: Check file path in rle_streamlit.py

## Key Files

- `lab/monitoring/hardware_monitor.py` - Core daemon (treat carefully)
- `lab/start_monitoring_suite.bat` - Main entry point
- `lab/README.md` - User-facing docs
- `README.md` (root) - Project overview

## Session Data Format

Each CSV row represents one sample (default 1 Hz):
- Timestamp: ISO UTC
- device: "gpu" or "cpu"
- rle_smoothed: Rolling 5-sample average
- E_th, E_pw: Split diagnostics
- rolling_peak: Adaptive reference (with decay)
- collapse: Binary flag (improved detection)
- alerts: Pipe-separated warnings (empty if none)

## Quick Reference

**Start monitoring**: `python start_monitor.py --mode gpu`
**Launch suite**: `start_monitoring_suite.bat`
**Analyze data**: `python analyze_session.py sessions/recent/[file].csv`
**View docs**: `lab/USAGE.md`

**Don't**: Break collapse detection, add heavyweight deps, modify Magic/
**Do**: Improve analysis tools, add visualizations, optimize monitoring

---

## Recent Changes (Session: 2025-10-27)

### Repository Setup
- Initialized git repository
- Added MIT License
- Created comprehensive .gitignore
- Pushed to GitHub: https://github.com/Nemeca99/RLE.git
- Repository contains organized lab structure and Magic/ project

### Lab Organization
- Organized project structure into `lab/` directory
- Moved stress tests → `lab/stress/`
- Moved analysis tools → `lab/analysis/`
- Moved monitoring tools → `lab/monitoring/`
- Session data → `lab/sessions/recent/`
- Archived screenshots → `lab/sessions/archive/screenshots/`

### New Tools
- `start_monitoring_suite.bat` - Launches monitor + Streamlit dashboard
- `rle_streamlit.py` - Real-time visualization dashboard
- `analyze_session.py` - Quick session statistics

### Improved Collapse Detection
Replaced simple 70% threshold with:
- Rolling peak decay (0.998 factor)
- Evidence requirements (thermal OR power)
- 7-second hysteresis
- 65% drop threshold (was 70%)
- Split E_th/E_pw diagnostics

Result: Reduced false positives from 51% → single digits.

### CSV Schema v2
Added columns: `E_th`, `E_pw`, `rolling_peak`
This breaks backward compatibility - old CSVs won't have these columns.

### Documentation & Tools (Session: 2025-10-27)
- Created `lab/docs/` directory with comprehensive guides
- `WHAT_IS_RLE.md` - Formula explained with worked examples
- `INTERPRETING_RESULTS.md` - How to analyze session data
- `ARCHITECTURE.md` - System flow diagrams and state machines
- Enhanced `analyze_session.py` with health assessment
- Added `batch_analyze.py` for multi-session comparison
- Updated README with CSV column reference table
- Created CHANGELOG.md for version tracking
- Added example baseline session CSV
- **RLE Formula Validation**: Independently verified by ChatGPT - formula computation matches logged values with <0.0001 precision across test samples
- **Agent Identity System**: Created `Kia.yaml` config, `kia_validate.py` with markdown reports and logging, added agent tracking to CHANGELOG

