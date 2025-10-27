# RLE Data Collection - What We're Recording

## Overview

RLE monitoring captures GPU/CPU telemetry at 1 Hz (1 sample per second). Each row is one second of hardware state.

## Data Categories

### 1️⃣ IDENTIFICATION & TIMESTAMPS

| Column | Type | Range | Purpose |
|--------|------|-------|---------|
| `timestamp` | ISO string | `2025-10-27T08:00:43.752965Z` | When sample was taken (UTC) |
| `device` | string | `"gpu"` or `"cpu"` | Which device measured |

**What it tells you:** Chronological order and device separation.

---

### 2️⃣ EFFICIENCY METRICS (RLE)

| Column | Type | Range | Purpose |
|--------|------|-------|---------|
| `rle_smoothed` | float | 0.0 - 2.0+ | 5-sample rolling avg RLE (primary metric) |
| `rle_raw` | float | 0.0 - 5.0+ | Instantaneous RLE (noisy) |
| `E_th` | float | 0.0 - 1.0 | Thermal efficiency component |
| `E_pw` | float | 0.0 - 5.0+ | Power efficiency component |
| `rolling_peak` | float | 0.0 - 2.0+ | Adaptive peak reference (for collapse detection) |

**What it tells you:**
- **High RLE (>0.8)**: System running efficiently
- **Medium RLE (0.3-0.8)**: Normal operation
- **Low RLE (<0.3)**: System stressed
- **E_th vs E_pw split**: Which is the bottleneck?

**Formula**: `RLE = (util × stability) / (a_load × (1 + 1/T_sustain))`

---

### 3️⃣ TEMPERATURE METRICS

| Column | Type | Range | Purpose |
|--------|------|-------|---------|
| `temp_c` | float | 30°C - 90°C | Core temperature (°C) |
| `vram_temp_c` | float | 30°C - 100°C | VRAM/memory junction temp (°C) |
| `t_sustain_s` | float | 1s - 600s | Seconds until thermal limit reached |

**What it tells you:**
- **<70°C**: Excellent cooling
- **70-80°C**: Good (normal gaming load)
- **80-85°C**: Hot (approaching limits)
- **>85°C**: Dangerous (thermal throttling)

**t_sustain interpretation:**
- **>300s**: Plenty of thermal headroom
- **60-300s**: Getting warm
- **<60s**: Very close to thermal throttling

---

### 4️⃣ POWER & PERFORMANCE METRICS

| Column | Type | Range | Purpose |
|--------|------|-------|---------|
| `power_w` | float | 0W - 220W | Power draw (Watts) |
| `util_pct` | float | 0% - 100% | GPU/CPU utilization percentage |
| `a_load` | float | 0.0 - 1.2 | Normalized load = power / rated power |
| `fan_pct` | int | 0% - 100% | Fan speed percentage |
| `gpu_clock_mhz` | int | 0 - 2000 | GPU core clock speed (MHz) |
| `mem_clock_mhz` | int | 0 - 10000 | Memory clock speed (MHz) |
| `mem_used_mb` | int | 0 - 8192 | VRAM used (MB) |
| `mem_total_mb` | int | varies | Total VRAM (MB) |
| `perf_state` | int | 0 - 31 | Performance state (P0-P31) |
| `throttle_reasons` | hex | varies | Bitmask of throttle reasons |
| `power_limit_w` | float | varies | GPU power limit (Watts) |

**What it tells you:**
- **util_pct**: How much of the GPU is working (0% idle, 100% maxed)
- **power_w**: Absolute power consumption
- **a_load**: Relative to GPU's power limit
  - **<0.8**: Not hitting power limits
  - **0.8-0.95**: Occasional power throttling
  - **>0.95**: Constantly power-limited
  - **>1.0**: Exceeding rated power (dangerous)

**fan_pct**: How hard cooling is working

**gpu_clock_mhz**: Core clock speed. Lower when throttled or idle

**mem_clock_mhz**: Memory clock speed. Usually fixed or decreases when power-limited

**mem_used_mb / mem_total_mb**: VRAM usage. High usage can impact performance

**perf_state**: GPU performance state (P0 = max, P8 = idle)

**throttle_reasons**: Hex bitmask showing why GPU throttled:
- `0x02000000` = Thermal slowdown (software)
- `0x04000000` = Thermal slowdown (hardware)
- `0x08000000` = Power brake slowdown
- Multiple bits set = multiple causes

**power_limit_w**: GPU's power limit (usually close to rated power)

---

### 5️⃣ COLLAPSE DETECTION METRICS

| Column | Type | Range | Purpose |
|--------|------|-------|---------|
| `collapse` | int | 0 or 1 | Collapse event flag |
| `rolling_peak` | float | varies | Adaptive peak for collapse detection |
| `alerts` | string | pipe-separated | Safety warnings |

**What it tells you:**

**`collapse = 1`** means:
- RLE dropped below 65% of recent peak
- For 7+ consecutive seconds
- With thermal OR power evidence
- System is losing efficiency

**`rolling_peak`**: The "normal" RLE the system established. Used to detect when efficiency drops.

**`alerts`** (example: `GPU_TEMP_LIMIT|VRAM_TEMP_LIMIT`):
- `GPU_TEMP_LIMIT`: Core temp ≥ 83°C for 5s
- `VRAM_TEMP_LIMIT`: VRAM temp ≥ 90°C for 5s
- `GPU_A_LOAD>1.10`: Exceeded rated power by 10%

**Collapse rate healthy ranges:**
- **0-5%**: Excellent (system efficient)
- **5-15%**: Moderate (some thermal stress)
- **>15%**: High (frequent efficiency loss, check cooling/power)

---

### 6️⃣ DIAGNOSTIC SPLIT (E_th vs E_pw)

| Component | Meaning | Low Value Causes |
|-----------|---------|------------------|
| **E_th** (Thermal) | How efficiently system manages thermal headroom | • Approaching temp limits<br>• Poor cooling<br>• Thermal throttling |
| **E_pw** (Power) | How efficiently power is converted to work | • Power limiting<br>• a_load > 0.95<br>• Not enough load |

**Examples:**

**Scenario A**: E_th low, E_pw high
→ Thermal bottleneck (cooling is the issue)

**Scenario B**: E_pw low, E_th high
→ Power bottleneck (hitting power limits)

**Scenario C**: Both low
→ Severely overstressed (both thermal and power limits)

---

## Data Collection Frequency

- **Sampling rate**: 1 Hz (1 sample per second)
- **CSV files**: Rotate hourly (new file each hour)
- **Duration**: Runs until you stop it (Ctrl+C)
- **File location**: `lab/sessions/recent/rle_YYYYMMDD_HH.csv`

---

## Understanding the CSV

Each row = 1 second snapshot of your GPU state

**Example row**:
```csv
2025-10-27T08:15:23.456789Z,gpu,0.723456,0.845678,0.580000,1.350000,75.00,82.00,198.50,99.00,0.993,310.0,80,1.001545,1,GPU_TEMP_LIMIT
```

Breaking it down:
- `timestamp`: When (08:15:23)
- `device`: GPU
- `rle_smoothed`: 0.72 (good efficiency)
- `temp_c`: 75°C (good)
- `power_w`: 198W (near limit)
- `util_pct`: 99% (maxed out)
- `a_load`: 0.993 (hitting power limit)
- `collapse`: 1 (efficiency dropped)
- `alerts`: GPU_TEMP_LIMIT (temp warning)

---

## Session Analysis

After capturing data, run:
```bash
python lab/analyze_session.py sessions/recent/rle_20251027_08.csv
```

This shows:
- Max/mean temp, power, RLE
- Collapse count and rate
- Health assessment
- Recommendations

---

## Key Relationships

### RLE Components
```
RLE = E_th × (util / a_load)
     └─┬─┘   └────┬──────┘
    Thermal    Power
     ratio      ratio
```

### When RLE Drops
RLE drops when EITHER:
1. **E_th drops** (thermal issues)
2. **util/a_load ratio drops** (power limiting or instability)

### Collapse Detection Triggers
All must be true:
- ✅ RLE < 65% of rolling peak
- ✅ For 7+ consecutive seconds
- ✅ Evidence: `t_sustain < 60s` OR `temp > (limit-5°C)` OR `a_load > 0.95`
- ✅ Under load: `util > 60%` OR `a_load > 0.75`
- ✅ Heating: temp rising >0.05°C/s

---

## Data Quality Indicators

**Good data**:
- Smooth temperature curves
- Collapse events rare (<5%)
- RLE correlates with utilization
- E_th and E_pw make sense (high during good conditions, low during stress)

**Bad data**:
- Constant collapse events (>50%) = detector too sensitive
- Never any collapses = detector too strict
- a_load > 1.1 = exceeds rated power (hardware issue)
- Temperature readings jump wildly = sensor issue

---

**Last Updated**: 2025-10-27  
**Agent**: Kia

