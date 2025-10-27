# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-10-27

### Agent Activity (Kia)
- Identified and fixed collapse detection false positives (51% → single digits)
- Created comprehensive documentation suite
- Designed and implemented batch analysis tools
- Validated RLE formula with external verification (ChatGPT)
- Organized lab structure for maintainability
- Added agent identity and personality parameters

### Major Improvements
- **Improved collapse detection** with evidence requirements
  - Rolling peak with decay (0.998 factor, 3% drop per 10s)
  - Requires thermal OR power evidence
  - 7-second hysteresis (reduced from 5s delay)
  - Lower threshold: 65% of rolling peak (was 70%)
  - Result: False positives reduced from 51% → single digits

### Added
- **Streamlit real-time dashboard** (`rle_streamlit.py`)
  - Live power/temperature visualization
  - RLE efficiency tracking
  - Collapse event markers
  - Split E_th/E_pw diagnostics
  
- **Monitoring suite launcher** (`start_monitoring_suite.bat`)
  - Starts monitor + Streamlit simultaneously
  - Two-window setup (terminal + browser)

- **Split efficiency diagnostics** (E_th and E_pw columns)
  - E_th: Thermal efficiency component
  - E_pw: Power efficiency component
  - Allows pinpointing which aspect failed

- **Rolling peak tracking** in CSV output
- **Lab organization**: Structured into `monitoring/`, `analysis/`, `stress/`, `sessions/`
- **Session analysis tool** (`analyze_session.py`) with health assessment
- **Batch analysis tool** (`scripts/batch_analyze.py`) for multi-session comparison
- **Comprehensive documentation suite** (`lab/docs/`)
  - `WHAT_IS_RLE.md` - Formula explained with worked examples
  - `INTERPRETING_RESULTS.md` - How to analyze session data
  - `ARCHITECTURE.md` - System flow diagrams and state machines
- **Example baseline session CSV** for testing analysis without hardware
- **CSV column reference table** in README

### Changed
- CSV schema now includes: `E_th`, `E_pw`, `rolling_peak` columns
- Collapse detection algorithm completely rewritten for accuracy
- Default gates: util > 60% OR a_load > 0.75 (was 50%/0.6)

### Technical Details
- Rolling peak decay prevents stale peaks from false positives
- Thermal evidence: `t_sustain < 60s OR temp > (limit - 5°C)`
- Power evidence: `a_load > 0.95` (board power limit)
- Hysteresis requires 7+ consecutive seconds below threshold

## [0.2.0] - 2025-10-26

### Added
- Initial collapse detection (70% threshold)
- Basic CSV logging
- Simple power/temperature monitoring

### Known Issues
- False positive rate: 51% (fixed in 0.3.0)

## [0.1.0] - 2025-10-25

### Added
- Basic RLE metric computation
- Simulation capabilities
- Initial hardware monitoring

---

[Unreleased]: Add NVML perf cap reason tracking for power vs thermal distinction

[0.3.0]: https://github.com/Nemeca99/RLE/releases/tag/v0.3.0
[0.2.0]: https://github.com/Nemeca99/RLE/releases/tag/v0.2.0
[0.1.0]: https://github.com/Nemeca99/RLE/releases/tag/v0.1.0

