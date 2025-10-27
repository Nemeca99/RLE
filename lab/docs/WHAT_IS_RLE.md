# What is RLE_real?

**RLE** (Recursive Load Efficiency) measures how efficiently your hardware is operating by balancing useful output against stress, waste, instability, and time-to-burnout.

## The Formula

```
RLE_real = (util × stability) / (A_load × (1 + 1/T_sustain))

E_th = stability / (1 + 1/T_sustain)  # Thermal efficiency
E_pw = util / A_load                    # Power efficiency
```

## Components Explained

### 1. **util** (Utilization)
The percentage of your GPU/CPU being used right now.
- High util = working hard
- Low util = idle/wasted

### 2. **stability** (Output Stability)
Measures how consistent your utilization is.
```
stability = 1 / (1 + utilization_standard_deviation)
```
- Smooth, steady load → high stability (≈1.0)
- Choppy, spiky load → low stability (<<1.0)

**Why it matters**: Erratic loads waste power on spin-up/spin-down. Smooth operation is more efficient.

### 3. **A_load** (Aggressive Load)
How hard you're pushing relative to rated capacity.
```
A_load = current_power / rated_power
```
- A_load = 0.5 → running at 50% of rated power
- A_load = 1.0 → maxing out board power
- A_load > 1.0 → exceeding rated specs (dangerous!)

**Why it matters**: Pulling more than rated power reduces efficiency and longevity. Operating near max throttles performance.

### 4. **T_sustain** (Time to Thermal Limit)
How long before you hit thermal limits at current temperature rise rate.
```
T_sustain = (temp_limit - current_temp) / (dT/dt)
```
Measured in seconds.

**Why it matters**: 
- High T_sustain (100s+) → lots of thermal headroom, can push harder
- Low T_sustain (<60s) → approaching thermal limits, must throttle
- When T_sustain → 0, you're thermal throttling

## Worked Example

**Scenario**: Playing a game, GPU monitoring shows:
- util = 85% (GPU working hard)
- power = 180W (out of 200W rated)
- temp = 70°C (limit is 83°C)
- temp rising at +1°C per second
- utilization over last 10s: [85, 88, 82, 84, 86, 83, 85, 87, 85, 84]

**Calculations:**

1. **A_load** = 180W / 200W = **0.90** (running at 90% of rated power)

2. **T_sustain** = (83°C - 70°C) / 1°C/s = **13 seconds**
   - You have 13 seconds before thermal throttle (if temp keeps rising)

3. **stability** = 1 / (1 + stddev([85,88,82,84,86,83,85,87,85,84]))
   - stddev = ~1.9%
   - stability = 1 / (1 + 1.9) = **0.34**
   - Relatively stable workload

4. **RLE** = (0.85 × 0.34) / (0.90 × (1 + 1/13))
   - = 0.289 / (0.90 × 1.077)
   - = 0.289 / 0.969
   - = **0.298**

**Interpretation**: 
- RLE = 0.298 is moderately efficient
- You're utilizing well (85%) with decent stability
- But you're close to power cap (90%) and have only 13s thermal headroom
- This is **productive but aggressive** operation

**Alternative scenario**: Same utilization but better thermals (temp at 55°C, T_sustain = 28s):
- RLE = 0.57 (much better!)
- Same work, lower stress = higher efficiency

## What High vs Low RLE Means

**High RLE (>0.5)**:
- Good utilization with stability
- Ample thermal headroom
- Operating well within power limits
- ✅ Efficient, sustainable operation

**Low RLE (<0.2)**:
- Either poor utilization (idle waste)
- OR pushing too hard (power/thermal limits)
- OR unstable workload (spiky performance)
- ⚠️ Inefficient or stressed operation

**Very low RLE (<0.1)**:
- Collapsing efficiency
- Thermal throttling likely
- Power limited
- 🔴 System is overstressed

## Visual Analogy

Think of RLE like engine efficiency in a car:

- **High RLE**: Highway cruising at optimal RPM (efficient, sustainable)
- **Medium RLE**: City driving with stop-and-go (waste energy on acceleration)
- **Low RLE**: Flooring it uphill in high gear (working hard, inefficient)
- **Collapse**: Engine overheating, forced to throttle back (failing efficiency)

RLE tells you if you're "cruising efficiently" or "wasting fuel fighting limits".

