# RLE Monitoring System Architecture

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     START MONITORING                         │
│         (start_monitoring_suite.bat or CLI)                  │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │   hardware_monitor.py daemon       │
         │   (Polling loop @ 1Hz)             │
         └───────────┬─────────────────────────┘
                     │
                     ├──────────┬──────────┬────────────┐
                     ▼          ▼          ▼            ▼
              ┌────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐
              │NVML    │ │ psutil │ │HWiNFO CSV│ │compute  │
              │(GPU)   │ │ (CPU)  │ │(optional)│ │RLE      │
              └────┬───┘ └────┬───┘ └────┬─────┘ └────┬────┘
                   │          │           │            │
                   └──────────┴───────────┴────────────┘
                                          │
                           ┌──────────────┴──────────────┐
                           ▼                             │
              ┌─────────────────────────┐       ┌──────────────┐
              │ Compute RLE_real:         │       │ Detect       │
              │                           │       │ Collapse:    │
              │  - util (NVML/psutil)     │       │  - Rolling   │
              │  - stability (stddev)    │       │    peak      │
              │  - A_load (power/rated)  │       │    decay     │
              │  - T_sustain (thermal)   │       │  - Evidence  │
              │                           │       │    required  │
              │  E_th = thermal eff      │       │  - 7s hyst. │
              │  E_pw = power eff        │       │              │
              └──────────┬────────────────┘       └──────┬───────┘
                         │                                │
                         └──────────┬─────────────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │  Rotating CSV Log   │
                         │  (hourly files)     │
                         │  rle_YYYYMMDD_HH.csv│
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
          ┌──────────────┐  ┌──────────────┐  ┌─────────────┐
          │ Streamlit    │  │  Analysis    │  │  Archive    │
          │ Real-time    │  │  Tools       │  │  (old data) │
          │ Dashboard    │  │  (pandas)    │  │             │
          │ (live view)  │  │  (reports)   │  │             │
          └──────────────┘  └──────────────┘  └─────────────┘
```

## Component Breakdown

### 1. Data Collection Layer
```
┌──────────────────────────────────────────────────┐
│                 Polling @ 1Hz                   │
├──────────────────────────────────────────────────┤
│ GPU:     NVML API → util, power, temp, fan       │
│ CPU:     psutil → util%, power (HWiNFO)           │
│ Temp:    NVML or HWiNFO CSV                      │
│ Power:   NVML (GPU), HWiNFO CSV (CPU)            │
└──────────────────────────────────────────────────┘
```

### 2. RLE Computation Pipeline
```
Raw Data → Compute Metrics → RLE Real → Collapse Check
   │            │               │              │
   │            ▼               ▼              ▼
   │     • stability          RLE       • Rolling peak
   │     • A_load        =  (util×stb)  • Evidence gate
   │     • T_sustain        / (A×(1+1/T))  • 7s hysteresis
   └──────────────────────────────────────────┘
                        ▼
              Log to CSV (with all components)
```

### 3. Collapse Detection Logic Flow
```
Sample arrives
    │
    ├─ Warm enough? (60s passed)
    │  NO → Skip detection
    │  YES →
    │      ├─ Rolling peak update (decay 0.998)
    │      │
    │      ├─ Smart gate check:
    │      │  • util > 60% OR a_load > 0.75
    │      │  • temp rising >0.05°C/s
    │      │
    │      ├─ Drop below 65% of rolling peak?
    │      │  NO → Reset counter
    │      │  YES → Increment counter (max 7)
    │      │
    │      ├─ Counter >= 7?
    │      │  NO → Not collapsed
    │      │  YES →
    │      │      ├─ Thermal evidence?
    │      │      │  (t_sustain < 60s OR temp > limit-5°C)
    │      │      │
    │      │      OR
    │      │      │
    │      │      └─ Power evidence?
    │      │         (a_load > 0.95)
    │      │
    │      └─ Evidence found → COLLAPSE = 1
    │         No evidence → COLLAPSE = 0
```

### 4. Session Data Flow
```
CSV Rotation (hourly):
  rle_20251027_04.csv  (hour 04)
  rle_20251027_05.csv  (hour 05)
  rle_20251027_06.csv  (hour 06)
         ↓
    ┌──────────────────┐
    │  sessions/recent/ │ (current)
    └──────────────────┘
         ↓ (manual move)
    ┌──────────────────┐
    │ sessions/archive/│ (historical)
    └──────────────────┘
```

## Performance Characteristics

- **Sampling rate**: 1 Hz (default, configurable 1-5 Hz)
- **CPU overhead**: <1% (lightweight daemon)
- **Memory**: ~50MB (Python process + data buffers)
- **CSV size**: ~2KB/minute (compressed ASCII)
- **Detection latency**: 7 seconds minimum (hysteresis)
- **File rotation**: Automatic (hourly)

## Key Design Decisions

### Why Rolling Peak?
Frozen peaks set during one scene make all future scenes look "collapsed". Rolling with decay adapts to actual hardware capability as it saturates.

### Why 7-Second Hysteresis?
Prevents noise from scene transitions. Games load new areas, transition menus, etc. Need sustained evidence of real efficiency loss.

### Why Evidence Required?
Without thermal/power evidence, you're just detecting workload changes, not efficiency problems. Proof is required.

### Why Split E_th/E_pw?
Allows diagnosis:
- If E_pw low: power-limited (boost power target or reduce load)
- If E_th low: thermal-limited (improve cooling)
- Both low: severely overstressed (reduce load)

## State Machine

```
┌──────────┐
│  Idle    │ (warmup period)
│ (T<60s)  │
└────┬─────┘
     │
     ▼ warmup complete
┌──────────┐
│  Ready   │
│ (tracking│───────┐
│  peak)   │       │
└────┬─────┘       │
     │             │
     ▼ under load  │ RLE >65% peak
┌──────────┐       │ reset counter
│ Checking │◄───────┘
│ for drop │       │
└────┬─────┘       │
     │ RLE <65% x 7s + evidence
     ▼
┌──────────┐
│Collapsed │
└──────────┘
```

## Integration Points

```
External APIs:
  ├── nvidia-ml-py3 (primary GPU data)
  ├── pynvml (fallback)
  ├── psutil (CPU metrics)
  └── HWiNFO CSV (optional CPU power/temp)

Outputs:
  ├── CSV logs (analysis)
  ├── Streamlit dashboard (real-time)
  └── analyze_session.py (statistics)
```

## Extension Points

Safe to extend:
- Add new CSV columns (append only)
- New analysis tools in `lab/analysis/`
- Additional plots in Streamlit
- More stress generators

Requires careful design:
- Modify collapse detection (affects false positive rate)
- Add new NVML sensors (may affect performance)
- Change sampling rate (affects detection latency)

