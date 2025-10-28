# RLE Master Document

## 1. Executive Summary
RLE (Recursive Load Efficiency) is a dimensionless, predictive, topology-invariant efficiency law for any thermal-work system. It quantifies how efficiently power is converted into useful work while preserving thermal stability. Validated across desktop CPU, desktop GPU, and mobile SoC.

- Cross-domain dispersion σ ≈ 0.16 (universal behavior)
- Predictive lead time: ~0.7–1.0 s before firmware throttling
- Mobile constants (S24 Ultra): collapse -0.0043 RLE/s, stabilization 0.0048 RLE/s, thermal sensitivity -0.2467 RLE/°C

See: [What is RLE](WHAT_IS_RLE.md) • [RLE Physics](RLE_PHYSICS.md) • [Mobile Validation](MOBILE_RLE_VALIDATION.md)

---

## 2. What is RLE (Detailed Overview)
RLE measures efficiency as a balance of productive work versus stress, waste, instability, and time-to-burnout. It is unitless, so values can be compared across devices and form factors.

Formula:
```
RLE = (util × stability) / (A_load × (1 + 1/T_sustain))
```
Components:
- util: utilization fraction (0–1)
- stability: 1 / (1 + stddev(util_recent)) — smooth loads are efficient
- A_load: actual_power / rated_power — how hard you’re pushing
- T_sustain: seconds to thermal limit at current dT/dt

Split diagnostics:
- E_th = stability / (1 + 1/T_sustain)  (thermal efficiency)
- E_pw = util / A_load                   (power efficiency)

Why it’s dimensionless: every factor is a ratio of like units or a pure number; units cancel.

See: [WHAT_IS_RLE.md](WHAT_IS_RLE.md) • [RLE_PHYSICS.md](RLE_PHYSICS.md)

---

## 3. Lab Overview (What the Lab Is)
The RLE Lab is a lightweight monitoring and analysis suite that:
- Samples GPU/CPU telemetry (~1 Hz)
- Computes RLE and diagnostics in real time
- Detects true efficiency collapses with evidence
- Logs to CSV for analysis and reporting
- Generates per-hour plots and session reports

Typical flow: Start monitor → Play/Run workload → CSV logs → Analyze/Report.

See: [GETTING_STARTED.md](GETTING_STARTED.md) • [USAGE.md](USAGE.md)

---

## 4. Folder Structure and Purpose
```
lab/
├─ monitoring/   # Daemons & live tools (keep <1% CPU)
│  ├─ hardware_monitor.py     # Core polling loop + RLE + collapse
│  ├─ rle_streamlit.py        # Live dashboard
│  └─ generate_report.py      # Auto report on shutdown
├─ analysis/     # Post-session tools
│  ├─ analyze_session.py      # Quick stats & health
│  ├─ rle_comprehensive_timeline.py  # Multi-session overlays
│  ├─ report_sessions.py      # Multi-page PDF reports
│  └─ summarize_sessions.py   # Batch CSV summaries
├─ stress/       # Load generators (safe, focused)
│  └─ simple_stress.py        # Example stress tool
├─ sessions/
│  ├─ recent/    # Hourly rotating CSVs (current)
│  └─ archive/   # Historical data & plots
└─ docs/         # Documentation (this folder)
```
Role of each area:
- monitoring/: measurement + real-time visualization
- analysis/: insight generation, plots, reports
- stress/: generate controlled load for testing
- sessions/: data lake of CSVs, split by recency
- docs/: user/developer documentation

See: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 5. Component Purposes & End-to-End Data Flow
High-level pipeline:
1) Collect → 2) Compute → 3) Detect → 4) Log → 5) Visualize/Analyze → 6) Report

- Collect: NVML (GPU), psutil (CPU), optional HWiNFO CSV for CPU power/temp
- Compute: util, stability, A_load, T_sustain → RLE, E_th, E_pw
- Detect: rolling_peak with decay; gates (util>60% or A_load>0.75); temp rising; 65% drop; 7s hysteresis; evidence (t_sustain<60s or temp>limit-5°C or A_load>0.95)
- Log: CSV rows at ~1 Hz (frozen schema v0.3.0)
- Visualize: Streamlit dashboard (live); matplotlib/PDF (post)
- Report: automatic summary on stop; on-demand PDF per-hour plots

See: [ARCHITECTURE.md](ARCHITECTURE.md) • [DATA_COLLECTION.md](DATA_COLLECTION.md) • [INTERPRETING_RESULTS.md](INTERPRETING_RESULTS.md)

---

## 6. Script & Equation Index (Deep Dives)
- Monitoring
  - `monitoring/hardware_monitor.py`: sampling, RLE compute, collapse detector
  - `monitoring/rle_streamlit.py`: live dashboard UI
  - `monitoring/generate_report.py`: end-of-session report
- Analysis
  - `analysis/analyze_session.py`: per-session stats/health
  - `analysis/rle_comprehensive_timeline.py`: multi-session overlays, knee points
  - `analysis/report_sessions.py`: per-hour multi-page PDF
  - `analysis/summarize_sessions.py`: batch CSV summary table
- Mobile (validation artifacts in lab/pc; docs here in docs/)
  - See: [MOBILE_RLE_VALIDATION.md](MOBILE_RLE_VALIDATION.md)
- Equations & Rationale
  - RLE definition and dimensional analysis: [RLE_PHYSICS.md](RLE_PHYSICS.md)
  - Component interpretations and thresholds: [WHAT_IS_RLE.md](WHAT_IS_RLE.md), [INTERPRETING_RESULTS.md](INTERPRETING_RESULTS.md)
  - Topology invariance: [TOPOLOGY_INVARIANCE.md](TOPOLOGY_INVARIANCE.md)
  - Publication package: [PUBLICATION.md](PUBLICATION.md)

---

## 7. Data Schema (CSV)
Schema v0.3.0 (frozen). Key groups:
- Identification: `timestamp`, `device`
- Efficiency: `rle_smoothed`, `rle_raw`, `E_th`, `E_pw`, `rolling_peak`
- Thermal: `temp_c`, `vram_temp_c`, `t_sustain_s`
- Power/Perf: `power_w`, `util_pct`, `a_load`, `fan_pct`
- Events: `collapse`, `alerts`
- Optional extended: clocks, perf state, throttle reasons, `cycles_per_joule`

See: [DATA_COLLECTION.md](DATA_COLLECTION.md) • [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 8. RLE Physics (Law)
Why RLE works across devices:
- Unitless ratios remove device-specific units
- Encodes thermal headroom (E_th) and power use (E_pw)
- Predicts collapse before firmware (lead time)

See: [RLE_PHYSICS.md](RLE_PHYSICS.md) • [WHAT_IS_RLE.md](WHAT_IS_RLE.md)

---

## 9. Mobile Validation (Galaxy S24 Ultra)
- Dataset: 1000 samples (16.7 min), 33→44.4°C, RLE 0.131–0.489
- Constants: collapse -0.0043 RLE/s; stabilization 0.0048 RLE/s; sensitivity -0.2467 RLE/°C
- Outcome: mobile overlaps desktop RLE ranges; predictive lead time <1 s

See: [MOBILE_RLE_VALIDATION.md](MOBILE_RLE_VALIDATION.md)

---

## 10. Topology Invariance
- Isolation (r ≈ 0) vs Coupling (r ≈ 0.47): RLE remains predictive
- No coupling assumption required; adapts to topology

See: [TOPOLOGY_INVARIANCE.md](TOPOLOGY_INVARIANCE.md)

---

## 11. Publication Package
- Methods summary, figures checklist, abstract
- Figures: predictive timeline, knee boundary, isolation vs coupling, efficiency ceiling

See: [PUBLICATION.md](PUBLICATION.md)

---

## 12. Usage & Troubleshooting
- Start monitor, view dashboard, generate reports
- Common issues: NVML loading, missing columns (pre-v0.3), dashboard path

See: [USAGE.md](USAGE.md) • [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 13. Glossary
- RLE: Recursive Load Efficiency (dimensionless efficiency index)
- E_th: Thermal efficiency component (headroom proxy)
- E_pw: Power efficiency component (util vs load)
- A_load: Aggressive load (power/rated)
- T_sustain: Time until thermal limit (s)
- Rolling peak: Adaptive reference for collapse detection
- Collapse: True, evidenced efficiency drop (not scene change)

---

## 14. Indices & Next Steps
- Docs Index: [INDEX.md](INDEX.md)
- Next Steps: stress tests, figure extraction, arXiv submission
- Changelog: [CHANGELOG.md](CHANGELOG.md)

---

## 15. Key Claims (One Page)
- Universal: same law across CPU/GPU/SoC, σ ≈ 0.16
- Predictive: 0.7–1.0 s lead time before firmware throttle
- Economic boundary: knee point defines efficient operating limit
- Dimensionless: comparable across power scales (4W→300W)

---

## 16. File Map (At a Glance)
- Master: this document (`RLE_Master.md`)
- Deep dives: WHAT_IS_RLE, ARCHITECTURE, DATA_COLLECTION, INTERPRETING_RESULTS, MOBILE_RLE_VALIDATION, TOPOLOGY_INVARIANCE, PUBLICATION, TROUBLESHOOTING, QUICK_REFERENCE, GETTING_STARTED, USAGE
