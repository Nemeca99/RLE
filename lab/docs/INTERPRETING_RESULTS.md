# How to Interpret RLE Results

This guide shows you what different patterns in your RLE session data mean.

## Common Scenarios

### 1. Healthy Gaming Session

**Pattern**: RLE stays between 0.3-0.8 for most of session

```
Power: 150-180W (moderate)
Temp: 60-72°C (comfortable)
RLE: 0.4-0.6 range
Collapse events: <5% of samples
```

**What it means**:
- GPU running at comfortable load
- Good thermal headroom
- Stable, efficient operation
- ✅ Everything working as designed

**What to do**: Nothing! This is ideal.

---

### 2. Thermal Saturation (Heavy Session)

**Pattern**: RLE starts high, gradually declines over time

```
Early session: RLE ≈ 0.7, temp ≈ 65°C
Mid session:  RLE ≈ 0.5, temp ≈ 75°C  
Late session: RLE ≈ 0.3, temp ≈ 78°C
Collapse events: Increasing in last third
```

**What it means**:
- System heating up during long session
- Less thermal headroom → lower T_sustain → lower RLE
- Efficiency degrades as heat builds
- Still functional, but not optimal

**What to do**:
- Check cooling (fans, thermal paste)
- Consider higher sample rate if you want to catch thermal ramps
- Note: Some decline over hours is normal

---

### 3. Power Limited (Pushing Hardware)

**Pattern**: RLE drops when hitting power cap

```
Power: Constantly 198-200W (maxed out)
Temp: 70-75°C (manageable)
RLE: Lower than similar temps elsewhere
E_pw: Very low (<0.5)
Collapse: Clustered during peak moments
```

**What it means**:
- GPU hitting board power limit, not thermal limit
- Power ICs saturated, can't deliver more
- Clocks dropped to stay within power budget
- Working hard, but power-limited not thermal-limited

**What to do**:
- Normal for aggressive games on 3060 Ti
- Only an issue if you want more FPS
- Consider undervolting to get more efficiency at same power
- Or upgrade to higher TDP GPU

---

### 4. Scene Change Chaos (False Positives - Old Detector)

**Pattern**: Rapid RLE swings, many collapse events

```
RLE: Spikes 0.8 → drops 0.1 → back 0.7 → down 0.05
Collapse events: 40-50% of samples
Temp: Stable
Power: Oscillating wildly
```

**What it means** (before v0.3 fix):
- Game constantly switching scenes (loading screens, menus, gameplay)
- Utilization jumps around
- Old detector flagged every scene switch as "collapse"
- NOT actually thermal problems, just workload variation

**What to do**:
- This is why we improved the detector
- New detector (v0.3+) requires evidence and will ignore scene changes

---

### 5. True Thermal Collapse

**Pattern**: Sustained low RLE with thermal evidence

```
RLE: 0.15-0.25 sustained for 30+ seconds
Temp: 78-82°C (approaching limit)
T_sustain: <10 seconds
Collapse: Clustered in this period
E_th: Dropping (thermal efficiency failing)
```

**What it means**:
- System genuinely overstressed
- Hitting thermal limits
- Clocks being throttled automatically
- Power/performance tradeoff forced

**What to do**:
- Take a break (let system cool)
- Improve cooling (case airflow, GPU fan curve)
- Reduce game settings
- Check thermal paste (if old GPU)
- This is the scenario we want to detect!

---

### 6. Efficiency Degradation

**Pattern**: Same workload, RLE decreases over identical scenes

```
Early game scene: RLE = 0.65
Replay same scene 30min later: RLE = 0.52
Replay again 1hr later: RLE = 0.43
Power/Temp: Same values
```

**What it means**:
- Thermal mass saturated
- Cumulative heat buildup
- Less efficient operation despite same load
- Hysteresis: system "remembering" previous stress

**What to do**:
- Document degradation rate
- Plan cooling improvements if unacceptable
- Normal for extended sessions
- Consider periodic cooldowns

---

## Split Component Diagnostics

### High E_th, Low E_pw
- Thermal efficiency good, power efficiency poor
- Not thermal throttled
- Likely power-limited
- → Boost clocks or reduce settings

### Low E_th, High E_pw  
- Thermal efficiency poor, power efficiency good
- Thermal bottleneck
- Cooling insufficient
- → Improve cooling

### Both Low
- Everything stressed
- Power AND thermal limits hit
- Heavily overworked
- → Reduce load or upgrade hardware

### Both High
- Everything optimal
- Perfect operating window
- Ideal efficiency
- → Keep doing what you're doing!

---

## Reading Your Session CSV

**Key columns to watch**:

| Column | What It Tells You |
|--------|-------------------|
| `rle_smoothed` | Overall efficiency (higher = better) |
| `E_th` | Thermal efficiency (higher = cooler) |
| `E_pw` | Power efficiency (higher = better util/load ratio) |
| `temp_c` | Current temperature (lower = better) |
| `t_sustain_s` | Seconds until thermal limit (higher = safer) |
| `a_load` | Normalized power (1.0 = max, >1.1 = danger) |
| `rolling_peak` | Best RLE seen (reference for collapse) |
| `collapse` | 1 = efficiency drop detected |

**Alerts column** flags:
- `GPU_TEMP_LIMIT` - Hit 83°C sustained
- `VRAM_TEMP_LIMIT` - VRAM hit 90°C  
- `GPU_A_LOAD>1.10` - Exceeding rated power dangerously

---

## Quick Decision Tree

```
Looking at your session data:

↓ Is RLE consistently >0.4?
├─ YES → Healthy operation, no action needed
│
└─ NO → Where is it failing?
    ├─ Low E_pw + a_load ≈ 1.0 → Power limited
    │    → Acceptable for max-performance mode
    │
    ├─ Low E_th + t_sustain < 30s → Thermal limited  
    │    → Improve cooling
    │
    ├─ Many collapse events → Check if v0.3+ detector
    │    → Old detector: ignore (false positives)
    │    → New detector: thermal/power problem
    │
    └─ Gradual decline over hours → Thermal saturation
         → Normal for extended sessions
```

## Example Analysis

From your recent gaming session:
```
Session: 26.6 minutes
Mean RLE: 0.17
Peak RLE: 1.00
Collapse Events: 819 (51% - before fix)

Interpretation:
- Bimodal load (idle vs maxed)
- Median power 184W (near cap)
- Max temp 76°C (safe)
- Mean RLE low due to scene changes (not thermal)
- Collapse count will be MUCH lower with v0.3 detector
```

Result: System healthy, detector was over-eager. New v0.3+ detector will reduce false positives significantly.

