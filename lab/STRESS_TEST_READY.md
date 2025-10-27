# Stress Test Ready

## What I've Added

✓ **CPU Frequency Tracking** (`cpu_freq_ghz`)
- Tracks CPU clock speed in GHz
- Using `psutil.cpu_freq()`

✓ **Clock Cycles per Joule** (`cycles_per_joule`)
- Calculated as: (CPU_freq_GHz × 1e9 × sample_time) / joules
- Represents computational efficiency (cycles per energy unit)

## Formula

```
clock_cycles_per_sample = CPU_freq_GHz × 1,000,000,000 × sample_time_sec
joules_per_sample = power_W × sample_time_sec
cycles_per_joule = clock_cycles_per_sample / joules_per_sample
```

**Interpretation**:
- Higher = more efficient (more cycles per unit energy)
- Lower = less efficient (fewer cycles per unit energy)
- Useful for comparing efficiency across different load levels

## Ready to Test

Once monitoring is running, I can start the stress test.

**Wait for your confirmation**, then run:
```bash
python stress\max_sustained_load.py --duration 30 --threads 8
```

**Expected outputs**:
- CSV will include `cpu_freq_ghz` and `cycles_per_joule` columns
- Watch `cycles_per_joule` drop at high thermal load (throttling)
- Compare efficiency across load levels

