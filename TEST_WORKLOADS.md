# GPU Test Workloads for RLE Refinement

## Current Status ✅

Monitor is running and logging to: `lab/sessions/recent/rle_20251027_08.csv`

## Test Strategy

To get solid data for refining RLE measurements, run these workloads:

### 1. Light Load (5 min)
**Goal**: Baseline idle/light load
- Just leave it running
- Or browse the web
- GPU should show 0-30% utilization

### 2. Steady AI Load (10 min) 
**Goal**: Consistent moderate load
```bash
python lab\stress\ai_sim_load.py --duration 10 --pattern steady
```
- GPU should hit 85-95% consistently
- Good for testing thermal buildup

### 3. Bursty AI Load (10 min)
**Goal**: Variable load (like real LLM inference)
```bash
python lab\stress\ai_sim_load.py --duration 10 --pattern bursty
```
- GPU oscillates 40-100%
- Tests collapse detection accuracy

### 4. Ramp-Up Load (10 min)
**Goal**: Thermal mass effects
```bash
python lab\stress\ai_sim_load.py --duration 10 --pattern ramp
```
- Starts at 50%, ramps to 95%
- Shows how RLE changes as temps rise

### 5. LM Studio Real Workload (15 min)
**Goal**: Real-world AI inference pattern
- Open LM Studio
- Load 7B-13B model
- Generate conversations continuously
- Real memory/compute patterns

### 6. Mixed Workload (20 min)
**Goal**: Realistic mixed usage
- 5 min light (web browsing)
- 5 min steady AI
- 5 min bursty AI
- 5 min LM Studio

## What to Look For in Data

After each session, check:
- **Collapse rate**: Should be <5% with v0.3 detector
- **RLE vs utilization**: High util → high RLE?
- **Thermal behavior**: Does temp stabilize?
- **Power limiting**: Is a_load hitting 1.0?
- **E_th vs E_pw**: Which efficiency dominates?

## Running Tests

**Option A: One test at a time**
```bash
# Terminal 1: Monitor running
start_monitor_simple.bat

# Terminal 2: Run test
python lab\stress\ai_sim_load.py --duration 10 --pattern steady
```

**Option B: Full test session**
```bash
# Monitor running in background
start_monitor_simple.bat

# Then run workloads sequentially:
python lab\stress\ai_sim_load.py --duration 5 --pattern steady
python lab\stress\ai_sim_load.py --duration 5 --pattern bursty
python lab\stress\ai_sim_load.py --duration 5 --pattern ramp

# All captured in one CSV
```

## After Each Test

Check the results:
```bash
python lab\analyze_session.py sessions\recent\rle_YYYYMMDD_HH.csv
```

## Expected Results

**Good session**:
- Collapse rate: 0-5%
- Max temp: <80°C
- RLE varies with workload (low during scene changes, high during steady load)
- E_th and E_pw split helps diagnose bottlenecks

**Bad session** (needs investigation):
- Collapse rate: >15%
- Temp over 80°C (thermal limiting)
- a_load > 1.05 (power limit exceeded)
- Consistent low RLE despite high util (inefficiency)

## Next Steps After Data Collection

1. **Compare sessions**: Use `python lab\scripts\batch_analyze.py sessions\recent/`
2. **Identify patterns**: When does RLE improve? When does it collapse?
3. **Refine thresholds**: Adjust collapse detection if needed
4. **Validate formula**: Does RLE correlate with observed efficiency?

