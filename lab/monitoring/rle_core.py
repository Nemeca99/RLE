#!/usr/bin/env python3
"""
RLE Core Engine
- Canonical formula (η, σ, α, τ) → RLE, E_th, E_pw
- Scaling model (power/temperature/time factors)
- Improved collapse detection (rolling peak, gates, hysteresis)
- Minimal control loop (decision states)
- CSV CLI: augment input CSV or simulate from simple columns

Usage:
  python lab/monitoring/rle_core.py --in sessions/recent/rle_YYYYMMDD_HH.csv --out out.csv
  python lab/monitoring/rle_core.py --help
"""

from __future__ import annotations
import argparse
import csv
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict

# ----------------------------
# Data classes
# ----------------------------
@dataclass
class RLEResult:
    # Primary
    rle_raw: float
    rle_smoothed: float
    e_th: float
    e_pw: float
    rle_norm: float
    # Components
    stability: float
    a_load: float
    t_sustain_s: float
    rolling_peak: float
    collapse: int
    # Optional diagnostics
    alerts: str = ""

@dataclass
class ControlDecision:
    state: str
    cpu_freq_limit_ghz: Optional[float] = None
    gpu_freq_limit_ghz: Optional[float] = None
    fan_speed_pct: Optional[int] = None
    power_limit_pct: Optional[int] = None
    workload_reduction_pct: Optional[int] = None

# ----------------------------
# Core engine
# ----------------------------
class RLECore:
    def __init__(self,
                 rated_power_w: float = 100.0,
                 temp_limit_c: float = 85.0,
                 max_t_sustain_s: float = 600.0,
                 smooth_n: int = 5,
                 # Collapse detection params
                 rolling_decay: float = 0.998, # ~3% per 10s at 1Hz
                 drop_frac: float = 0.65,
                 hysteresis_s: int = 7,
                 util_gate_pct: float = 60.0,
                 a_load_gate: float = 0.75):
        self.rated_power_w = rated_power_w
        self.temp_limit_c = temp_limit_c
        self.max_t_sustain_s = max_t_sustain_s
        self.smooth_n = max(1, int(smooth_n))
        self.rolling_decay = rolling_decay
        self.drop_frac = drop_frac
        self.hysteresis_s = hysteresis_s
        self.util_gate_pct = util_gate_pct
        self.a_load_gate = a_load_gate

        self.util_hist: List[float] = []
        self.temp_hist: List[float] = []
        self.rle_hist: List[float] = []
        self.rolling_peak: float = 0.0
        self.below_ctr: int = 0

    def _rolling_mean(self, data: List[float], n: int) -> float:
        if not data: return 0.0
        if len(data) <= n: return sum(data)/len(data)
        return sum(data[-n:]) / float(n)

    def _rolling_stdev(self, data: List[float], n: int) -> float:
        if len(data) < 2: return 0.0
        window = data[-n:] if len(data) >= n else data
        return statistics.pstdev(window)

    def compute_components(self, util_pct: float, temp_c: Optional[float], power_w: Optional[float], dt_s: float = 1.0) -> Dict[str, float]:
        # Histories
        self.util_hist.append(max(0.0, min(100.0, util_pct)))
        if temp_c is not None:
            self.temp_hist.append(temp_c)

        # Utilization η
        eta = (self.util_hist[-1] / 100.0) if self.util_hist else 0.0

        # Stability σ (inverse of rolling std dev over last 5 samples)
        stdev = self._rolling_stdev(self.util_hist, n=5)
        stability = 1.0 / (1.0 + stdev)

        # Load factor α
        p = power_w if (power_w is not None and power_w > 0) else (self.rated_power_w * eta)
        a_load = p / max(self.rated_power_w, 1e-6)

        # Sustainability time τ (RC thermal model inspired)
        t_sustain = self.compute_t_sustain(self.temp_limit_c, self.temp_hist, dt_s, self.max_t_sustain_s)

        return dict(eta=eta, stability=stability, a_load=a_load, t_sustain=t_sustain)

    @staticmethod
    def compute_t_sustain(temp_limit_c: float, temp_hist: List[float], dt_s: float, max_t: float) -> float:
        if len(temp_hist) < 2:
            return max_t
        dT = temp_hist[-1] - temp_hist[-2]
        dTdt = max(dT / max(dt_s, 1e-3), 1e-3)
        t_sustain = (temp_limit_c - temp_hist[-1]) / dTdt
        return max(min(t_sustain, max_t), 1.0)

    def compute_rle(self, util_pct: float, temp_c: Optional[float], power_w: Optional[float], dt_s: float = 1.0) -> RLEResult:
        c = self.compute_components(util_pct, temp_c, power_w, dt_s)
        eta = c['eta']; stability = c['stability']; a_load = c['a_load']; t_sustain = c['t_sustain']
        denom = max(a_load, 1e-6) * (1.0 + 1.0 / max(t_sustain, 1e-6))
        rle_raw = (eta * stability) / denom
        rle_smooth = self._smooth_rle(rle_raw)

        # Diagnostics
        e_th = stability / (1.0 + 1.0 / max(t_sustain, 1e-6))
        e_pw = eta / max(a_load, 1e-6)
        rle_norm = self.normalize_rle(rle_smooth, util_pct)

        # Collapse detection
        collapsed = self._detect_collapse(rle_smooth, util_pct, a_load, temp_c, t_sustain)

        return RLEResult(
            rle_raw=rle_raw,
            rle_smoothed=rle_smooth,
            e_th=e_th,
            e_pw=e_pw,
            rle_norm=rle_norm,
            stability=stability,
            a_load=a_load,
            t_sustain_s=t_sustain,
            rolling_peak=self.rolling_peak,
            collapse=collapsed,
            alerts=""
        )

    def _smooth_rle(self, rle_raw: float) -> float:
        self.rle_hist.append(rle_raw)
        return self._rolling_mean(self.rle_hist, self.smooth_n)

    def _detect_collapse(self, rle_sm: float, util_pct: float, a_load: float, temp_c: Optional[float], t_sustain: float) -> int:
        # Warm-up: require a few samples before enabling
        warm = len(self.rle_hist) >= max(self.smooth_n, 5)
        if not warm:
            self.rolling_peak = 0.0
            self.below_ctr = 0
            return 0

        # Rolling peak with decay
        self.rolling_peak = max(rle_sm, self.rolling_peak * self.rolling_decay)

        # Gates
        under_load = (util_pct > self.util_gate_pct) or (a_load > self.a_load_gate)
        heating = False
        if len(self.temp_hist) >= 2 and temp_c is not None:
            heating = (self.temp_hist[-1] - self.temp_hist[-2]) > 0.05
        gate = under_load and heating

        # Hysteresis
        drop = rle_sm < (self.drop_frac * max(self.rolling_peak, 1e-6))
        if gate and drop:
            self.below_ctr += 1
        else:
            self.below_ctr = 0

        collapsed_flag = self.below_ctr >= self.hysteresis_s

        # Evidence requirement
        thermal_evidence = (t_sustain < 60) or (temp_c is not None and temp_c > (self.temp_limit_c - 5))
        power_evidence = (a_load > 0.95)

        return 1 if (collapsed_flag and (thermal_evidence or power_evidence)) else 0

    # ----------------------------
    # Normalization & scaling
    # ----------------------------
    @staticmethod
    def normalize_rle(rle: float, util_pct: float, device_type: str = "cpu") -> float:
        # Same shape as hardware_monitor; keep consistent
        if device_type == "cpu":
            baseline = 0.3; optimal = 5.0; peak_load = 67.0
        else:
            baseline = 0.1; optimal = 3.0; peak_load = 60.0
        u = max(0.0, min(100.0, util_pct))
        if u <= peak_load:
            expected = baseline + (optimal - baseline) * (u / peak_load)
        else:
            expected = optimal - (optimal - baseline * 0.5) * ((u - peak_load) / (100 - peak_load))
        return max(0.0, min(1.0, rle / max(expected, 1e-6)))

    @staticmethod
    def scale_rle(rle: float, p_actual_w: float, t_actual_c: float,
                  p_ref_w: float = 100.0, t_ref_c: float = 60.0,
                  beta: float = 0.12, gamma: float = 0.08,
                  tau_actual_s: Optional[float] = None, tau_ref_s: float = 300.0, delta: float = 0.10) -> float:
        """Apply cross-domain scaling from RLE_SCALING_MODEL.md"""
        if p_actual_w <= 0 or t_actual_c <= 0:
            return rle
        factor = (p_ref_w / p_actual_w) ** beta * (t_ref_c / t_actual_c) ** gamma
        if tau_actual_s is not None and tau_actual_s > 0:
            factor *= (tau_ref_s / tau_actual_s) ** delta
        return rle * factor

    # ----------------------------
    # Control decisions
    # ----------------------------
    def control_decision(self, rle_current: float, rle_predicted: Optional[float] = None, thermal_headroom_c: Optional[float] = None) -> ControlDecision:
        pred = rle_predicted if (rle_predicted is not None) else rle_current
        # Adjust fan suggestion by headroom if provided
        headroom_bonus = 0
        if thermal_headroom_c is not None and thermal_headroom_c > 5:
            headroom_bonus = -10  # slightly less aggressive fans if ample headroom
        if rle_current < 0.2 or pred < 0.1:
            return ControlDecision('emergency', 0.8, 0.2, max(0, 100 + headroom_bonus), 50, 50)
        elif rle_current < 0.4 or pred < 0.3:
            return ControlDecision('aggressive', 1.2, 0.5, max(0, 80 + headroom_bonus), 70, 25)
        elif rle_current < 0.6 or pred < 0.5:
            return ControlDecision('moderate', 2.5, 0.9, max(0, 60 + headroom_bonus), 85, 10)
        else:
            return ControlDecision('maintain', None, None, None, None, None)

# ----------------------------
# CSV CLI
# ----------------------------

def augment_csv(in_path: Path, out_path: Path, rated_power_w: float, temp_limit_c: float) -> None:
    core = RLECore(rated_power_w=rated_power_w, temp_limit_c=temp_limit_c)
    with in_path.open('r', newline='', encoding='utf-8', errors='ignore') as f_in, out_path.open('w', newline='', encoding='utf-8') as f_out:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames or [])
        # Add outputs if missing
        for col in [
            'rle_smoothed','rle_raw','rle_norm','E_th','E_pw','temp_c','power_w','util_pct','a_load','t_sustain_s',
            'rolling_peak','collapse','alerts'
        ]:
            if col not in fieldnames:
                fieldnames.append(col)
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        prev_ts = None
        for row in reader:
            # Try to read inputs; fall back if missing
            util = _to_float(row.get('util_pct')) or _to_float(row.get('cpu_util_pct')) or 0.0
            temp = _to_float(row.get('temp_c')) or _to_float(row.get('battery_temp_c'))
            power = _to_float(row.get('power_w'))

            # dt estimate (assume 1.0 if unknown)
            dt = 1.0
            cur_ts = row.get('timestamp')
            if prev_ts is not None and cur_ts == prev_ts:
                dt = 1.0
            prev_ts = cur_ts

            res = core.compute_rle(util, temp, power, dt)

            # Write augmented row
            row['rle_raw'] = f"{res.rle_raw:.6f}"
            row['rle_smoothed'] = f"{res.rle_smoothed:.6f}"
            row['rle_norm'] = f"{res.rle_norm:.6f}"
            row['E_th'] = f"{res.e_th:.6f}"
            row['E_pw'] = f"{res.e_pw:.6f}"
            row['a_load'] = f"{res.a_load:.6f}"
            row['t_sustain_s'] = f"{res.t_sustain_s:.1f}"
            row['rolling_peak'] = f"{res.rolling_peak:.6f}"
            row['collapse'] = res.collapse
            row['alerts'] = res.alerts
            # Ensure temp/power/util columns are present for downstream tools
            if 'temp_c' not in row or row['temp_c'] in (None, ''):
                row['temp_c'] = '' if temp is None else f"{temp:.2f}"
            if 'util_pct' not in row or row['util_pct'] in (None, ''):
                row['util_pct'] = f"{util:.2f}"
            if 'power_w' not in row or row['power_w'] in (None, ''):
                row['power_w'] = '' if power is None else f"{power:.2f}"

            writer.writerow(row)


def _to_float(x) -> Optional[float]:
    try:
        if x is None: return None
        s = str(x).strip()
        if s == '' or s.lower() == 'none': return None
        return float(s)
    except (ValueError, TypeError):
        return None

# ----------------------------
# CLI
# ----------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="RLE Core Engine - augment CSVs with canonical RLE metrics")
    p.add_argument('--in', dest='infile', type=str, required=True, help='Input CSV (must have timestamp and util/temp/power columns if available)')
    p.add_argument('--out', dest='outfile', type=str, required=True, help='Output CSV path')
    p.add_argument('--rated-power', dest='rated_power', type=float, default=100.0, help='Baseline/rated power for A_load normalization (W)')
    p.add_argument('--temp-limit', dest='temp_limit', type=float, default=85.0, help='Thermal limit (°C) used by T_sustain')
    return p.parse_args()


def main() -> None:
    args = parse_args()
    in_path = Path(args.infile)
    out_path = Path(args.outfile)
    augment_csv(in_path, out_path, rated_power_w=args.rated_power, temp_limit_c=args.temp_limit)
    print(f"Wrote augmented CSV → {out_path}")


if __name__ == '__main__':
    main()
