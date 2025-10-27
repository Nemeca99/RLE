import argparse, csv, os, time, statistics
from datetime import datetime
import psutil

# NVML (GPU)
try:
    # Import pynvml (works with nvidia-ml-py backend)
    import pynvml
    from pynvml import (
        nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates,
        nvmlDeviceGetPowerUsage, nvmlDeviceGetTemperature, nvmlDeviceGetFanSpeed,
        nvmlDeviceGetComputeRunningProcesses
    )
    # Constants for temperature sensors
    # NVML_TEMPERATURE_GPU = 0 (core temp)
    # NVML_TEMPERATURE_MEMORY = 1 (memory junction)
    NVML_TEMPERATURE_GPU = 0
    NVML_TEMPERATURE_MEMORY = 1
    NVML_OK = True
except Exception as e:
    NVML_OK = False
    print(f"NVML import failed: {e}")

# ----------------------------
# Config defaults (tweakable)
# ----------------------------
DEFAULTS = dict(
    rated_gpu_w = 200.0,   # 3060 Ti board power ballpark
    rated_cpu_w = 125.0,   # your sustained CPU power (PL1-ish)
    gpu_temp_limit = 83.0,
    vram_temp_limit = 90.0,
    cpu_temp_limit = 80.0,
    warmup_sec = 60,
    collapse_drop_frac = 0.70,
    collapse_sustain_sec = 5,
    load_gate_util_pct = 50.0,
    load_gate_a_load = 0.60,
    sample_hz = 1,
    smooth_n = 5,
    max_t_sustain = 600.0
)

# ----------------------------
# Utilities
# ----------------------------
class Rolling:
    def __init__(self, n):
        self.n = n
        self.buf = []

    def add(self, x):
        self.buf.append(x)
        if len(self.buf) > self.n:
            self.buf.pop(0)

    def last(self, k=1):
        return self.buf[-k:] if k>1 else (self.buf[-1] if self.buf else None)

    def mean(self, k=None):
        data = self.buf if k is None else self.last(k)
        return sum(data)/len(data) if data else 0.0

    def stdev(self, k=None):
        data = self.buf if k is None else self.last(k)
        if not data or len(data) < 2: return 0.0
        return statistics.pstdev(data)

def below_normal_priority():
    try:
        p = psutil.Process()
        if os.name == "nt":
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        else:
            p.nice(10)
    except Exception:
        pass

def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def rotate_writer(base_dir):
    ensure_dir(base_dir)
    current_key = None
    fh, writer = None, None
    def get():
        nonlocal current_key, fh, writer
        key = datetime.utcnow().strftime("%Y%m%d_%H")
        if key != current_key:
            if fh: fh.close()
            fname = os.path.join(base_dir, f"rle_{key}.csv")
            new_file = not os.path.exists(fname)
            fh = open(fname, "a", newline="", buffering=1)
            writer = csv.writer(fh)
            if new_file:
                writer.writerow(["timestamp","device","rle_smoothed","rle_raw","E_th","E_pw","temp_c","vram_temp_c",
                                 "power_w","util_pct","a_load","t_sustain_s","fan_pct","rolling_peak","collapse","alerts"])
            current_key = key
        return writer
    return get

# ----------------------------
# HWiNFO CSV tail (optional)
# ----------------------------
class HwinfoCsvTail:
    """
    Lightweight CSV tailer. Expects HWiNFO to roll files or append rows with timestamps.
    You pass target column names you'd like; we try to map fuzzy names.
    """
    def __init__(self, path, target_cols=None):
        self.path = path
        self.last_pos = 0
        self.header = None
        self.col_index = {}
        self.target_cols = target_cols or []

    def _scan_header(self):
        try:
            with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
                head = f.readline()
                if not head: return False
                self.header = [h.strip() for h in head.strip().split(",")]
                # fuzzy map: lower no spaces
                canon = {h.lower().replace(" ", ""): i for i,h in enumerate(self.header)}
                self.col_index = {}
                for want in self.target_cols:
                    key = want.lower().replace(" ", "")
                    # best-effort: exact or contains
                    match = None
                    if key in canon:
                        match = canon[key]
                    else:
                        for k,i in canon.items():
                            if key in k:
                                match = i; break
                    if match is not None:
                        self.col_index[want] = match
                return True
        except Exception:
            return False

    def latest(self):
        if not self.path or not os.path.exists(self.path): return {}
        if self.header is None:
            if not self._scan_header(): return {}
        # read last non-empty line
        try:
            with open(self.path, "rb") as f:
                try:
                    f.seek(-4096, os.SEEK_END)
                except OSError:
                    f.seek(0)
                chunk = f.read().decode("utf-8", errors="ignore")
            lines = [ln for ln in chunk.strip().splitlines() if ln.strip()]
            if not lines: return {}
            last = lines[-1]
            parts = [p.strip() for p in last.split(",")]
            out = {}
            for want, idx in self.col_index.items():
                if idx < len(parts):
                    try:
                        out[want] = float(parts[idx])
                    except:
                        out[want] = None
            return out
        except Exception:
            return {}

# ----------------------------
# NVML helpers
# ----------------------------
class GpuNVML:
    def __init__(self):
        if not NVML_OK:
            raise RuntimeError("NVML not available")
        nvmlInit()
        self.handle = nvmlDeviceGetHandleByIndex(0)

    def poll(self):
        h = self.handle
        util = nvmlDeviceGetUtilizationRates(h).gpu  # %
        power = nvmlDeviceGetPowerUsage(h) / 1000.0  # W
        temp_core = nvmlDeviceGetTemperature(h, NVML_TEMPERATURE_GPU)  # °C
        # Try memory/junction temp if supported
        vram_temp = None
        try:
            vram_temp = nvmlDeviceGetTemperature(h, NVML_TEMPERATURE_MEMORY)
        except Exception:
            vram_temp = None
        try:
            fan = nvmlDeviceGetFanSpeed(h)  # %
        except Exception:
            fan = 0
        return dict(util=util, power=power, temp_core=temp_core, temp_vram=vram_temp, fan=fan)

# ----------------------------
# RLE computation
# ----------------------------
def compute_t_sustain(temp_limit, temp_hist, dt, max_t=600.0):
    if len(temp_hist) < 2: return max_t
    dT = temp_hist[-1] - temp_hist[-2]
    dTdt = max(dT / max(dt, 1e-3), 1e-3)
    t_sustain = (temp_limit - temp_hist[-1]) / dTdt
    return max(min(t_sustain, max_t), 1.0)

def compute_rle(util_hist, temp_hist, q_in_w, a_load, temp_limit, dt, max_t=600.0):
    util = (util_hist[-1] / 100.0) if util_hist else 0.0
    stability = 1.0 / (1.0 + (statistics.pstdev(util_hist[-10:]) if len(util_hist) >= 5 else 0.0))
    t_sustain = compute_t_sustain(temp_limit, temp_hist, dt, max_t=max_t)
    denom = max(a_load, 1e-3) * (1.0 + 1.0 / t_sustain)
    # q_in_w is intentionally unused - available for future use
    rle = (util * stability) / denom
    
    # Split into thermal and power components for diagnosis
    E_th = stability / (1.0 + 1.0 / t_sustain)
    E_pw = util / max(a_load, 1e-3)
    
    return rle, t_sustain, E_th, E_pw

# ----------------------------
# Monitor
# ----------------------------
def monitor(args):
    below_normal_priority()
    tick = 1.0 / max(1, int(args.sample_hz))
    # Write to sessions/recent/ directory
    writer_get = rotate_writer("sessions/recent")

    # HWiNFO CSV tail (optional)
    hw_targets = [
        "GPU Memory Junction Temperature",  # vram temp
        "CPU Package Power",                # W
        "CPU Package",                      # temp C (sometimes named like this)
        "CPU (Tctl/Tdie)",                  # alt temp name
        "GPU Memory Usage"                  # optional VRAM used
    ]
    hw = HwinfoCsvTail(args.hwinfo_csv, target_cols=hw_targets) if args.hwinfo_csv else None

    gpu = None
    gpu_util_hist = None
    gpu_temp_hist = None
    rle_hist_gpu = None
    gpu_peak = 0.0
    gpu_below_ctr = 0
    gpu_peak_val = 0.0  # For tracking rolling peak
    
    if args.mode in ("gpu","both"):
        if not NVML_OK:
            raise RuntimeError("GPU mode requested but NVML not available.")
        gpu = GpuNVML()
        gpu_util_hist = Rolling(120)
        gpu_temp_hist = Rolling(120)
        rle_hist_gpu = Rolling(args.smooth_n)

    cpu_util_hist = Rolling(120)
    cpu_temp_hist = Rolling(120)  # only filled if we get temps
    rle_hist_cpu = Rolling(args.smooth_n)
    cpu_peak = 0.0
    cpu_below_ctr = 0

    start = time.time()

    while True:
        ts = now_iso()
        alerts = []
        tnow = time.time()
        warm = (tnow - start) > args.warmup_sec

        # -------- GPU --------
        if gpu and gpu_util_hist and gpu_temp_hist and rle_hist_gpu:
            g = gpu.poll()
            g_util = g["util"] or 0.0
            g_power = g["power"] or 0.0
            g_temp = g["temp_core"] or 0.0
            g_vram_temp = g["temp_vram"]
            g_fan = g["fan"] or 0

            # If no VRAM temp from NVML, try HWiNFO CSV
            if g_vram_temp is None and hw:
                latest = hw.latest()
                v = latest.get("GPU Memory Junction Temperature")
                if v is not None: g_vram_temp = v

            gpu_util_hist.add(g_util)
            gpu_temp_hist.add(g_temp)
            a_load_gpu = (g_power / args.rated_gpu) if args.rated_gpu>0 else 0.0
            rle_raw_gpu, t_sus_gpu, e_th_gpu, e_pw_gpu = compute_rle(
                gpu_util_hist.buf, gpu_temp_hist.buf, g_power, a_load_gpu, args.gpu_temp_limit, tick, DEFAULTS['max_t_sustain']
            )
            rle_hist_gpu.add(rle_raw_gpu)
            rle_sm_gpu = rle_hist_gpu.mean()

            # Improved collapse detection with rolling peak and hysteresis
            collapsed_gpu = 0
            gpu_peak_val = gpu_peak if warm else 0.0  # For logging
            if warm:
                # Rolling peak with decay (0.998 = 3% drop per 10s at 1Hz)
                gpu_peak = max(rle_sm_gpu, gpu_peak * 0.998)
                gpu_peak_val = gpu_peak  # For logging
                
                # Smart gate: require real load AND heating
                under_load = (g_util > 60) or (a_load_gpu > 0.75)
                heating = (len(gpu_temp_hist.buf) >= 2) and (gpu_temp_hist.buf[-1] - gpu_temp_hist.buf[-2] > 0.05)
                gate = under_load and heating
                
                # Two-stage hysteresis with recovery
                drop = rle_sm_gpu < 0.65 * gpu_peak
                if gate and drop:
                    gpu_below_ctr += 1
                else:
                    gpu_below_ctr = 0
                
                collapsed_flag = gpu_below_ctr >= 7
                
                # Require thermal or power evidence
                thermal_evidence = (t_sus_gpu < 60) or (g_temp > (args.gpu_temp_limit - 5))
                # TODO: track NVML perf cap reasons if available
                # For now, power-capped is inferred from a_load near 1.0
                power_capped = (a_load_gpu > 0.95)
                
                collapsed_gpu = 1 if (collapsed_flag and (thermal_evidence or power_capped)) else 0

            # Safety alerts (log-only)
            if g_temp >= args.gpu_temp_limit:
                alerts.append("GPU_TEMP_LIMIT")
            if g_vram_temp is not None and g_vram_temp >= args.vram_temp_limit:
                alerts.append("VRAM_TEMP_LIMIT")
            if a_load_gpu > 1.10:
                alerts.append("GPU_A_LOAD>1.10")

            w = writer_get()
            w.writerow([ts,"gpu",f"{rle_sm_gpu:.6f}",f"{rle_raw_gpu:.6f}",
                        f"{e_th_gpu:.6f}", f"{e_pw_gpu:.6f}", f"{g_temp:.2f}", f"{'' if g_vram_temp is None else f'{g_vram_temp:.2f}'}",
                        f"{g_power:.2f}", f"{g_util:.2f}", f"{a_load_gpu:.3f}",
                        f"{t_sus_gpu:.1f}", f"{g_fan}", f"{gpu_peak_val:.6f}", collapsed_gpu, "|".join(alerts)])

        # -------- CPU --------
        if args.mode in ("cpu","both"):
            c_util = psutil.cpu_percent(interval=None)
            c_power = None
            c_temp = None
            if hw:
                latest = hw.latest()
                pw = latest.get("CPU Package Power")
                if pw is not None: c_power = pw
                # Try temps in likely fields
                for key in ("CPU Package","CPU (Tctl/Tdie)"):
                    tv = latest.get(key)
                    if tv is not None:
                        c_temp = tv
                        break

            cpu_util_hist.add(c_util)
            if c_temp is not None: cpu_temp_hist.add(c_temp)
            # If we have no temp history, synthesize a flat line to keep math stable
            temp_hist = cpu_temp_hist.buf if cpu_temp_hist.buf else [40.0, 40.0]

            a_load_cpu = ( (c_power or 0.0) / args.rated_cpu ) if args.rated_cpu>0 else 0.0
            rle_raw_cpu, t_sus_cpu, e_th_cpu, e_pw_cpu = compute_rle(
                cpu_util_hist.buf, temp_hist, (c_power or 0.0), a_load_cpu,
                args.cpu_temp_limit, tick, DEFAULTS['max_t_sustain']
            )
            rle_hist_cpu.add(rle_raw_cpu)
            rle_sm_cpu = rle_hist_cpu.mean()

            # Improved collapse detection with rolling peak and hysteresis
            collapsed_cpu = 0
            cpu_peak_val = cpu_peak if warm else 0.0  # For logging
            if warm:
                # Rolling peak with decay
                cpu_peak = max(rle_sm_cpu, cpu_peak * 0.998)
                cpu_peak_val = cpu_peak  # For logging
                
                # Smart gate: require real load AND heating
                under_load = (c_util > 60) or (a_load_cpu > 0.75)
                heating = (len(temp_hist) >= 2) and (temp_hist[-1] - temp_hist[-2] > 0.05)
                gate = under_load and heating
                
                # Two-stage hysteresis
                drop = rle_sm_cpu < 0.65 * cpu_peak
                if gate and drop:
                    cpu_below_ctr += 1
                else:
                    cpu_below_ctr = 0
                
                collapsed_flag = cpu_below_ctr >= 7
                
                # Require thermal or power evidence
                thermal_evidence = (t_sus_cpu < 60) or (c_temp is not None and c_temp > (args.cpu_temp_limit - 5))
                power_capped = (a_load_cpu > 0.95)
                
                collapsed_cpu = 1 if (collapsed_flag and (thermal_evidence or power_capped)) else 0

            alerts_cpu = []
            if c_temp is not None and c_temp >= args.cpu_temp_limit:
                alerts_cpu.append("CPU_TEMP_LIMIT")
            if a_load_cpu > 1.10:
                alerts_cpu.append("CPU_A_LOAD>1.10")

            w = writer_get()
            w.writerow([ts,"cpu",f"{rle_sm_cpu:.6f}",f"{rle_raw_cpu:.6f}",
                        f"{e_th_cpu:.6f}", f"{e_pw_cpu:.6f}", f"{'' if c_temp is None else f'{c_temp:.2f}'}","",
                        f"{'' if c_power is None else f'{c_power:.2f}'}", f"{c_util:.2f}", f"{a_load_cpu:.3f}",
                        f"{t_sus_cpu:.1f}","", f"{cpu_peak_val:.6f}", collapsed_cpu, "|".join(alerts_cpu)])

        # Sleep
        time.sleep(tick)

# ----------------------------
# CLI
# ----------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Background RLE_real monitor")
    p.add_argument("--mode", choices=["gpu","cpu","both"], default="gpu")
    p.add_argument("--sample-hz", type=int, default=DEFAULTS['sample_hz'])
    p.add_argument("--rated-gpu", type=float, default=DEFAULTS['rated_gpu_w'])
    p.add_argument("--rated-cpu", type=float, default=DEFAULTS['rated_cpu_w'])
    p.add_argument("--gpu-temp-limit", type=float, default=DEFAULTS['gpu_temp_limit'])
    p.add_argument("--vram-temp-limit", type=float, default=DEFAULTS['vram_temp_limit'])
    p.add_argument("--cpu-temp-limit", type=float, default=DEFAULTS['cpu_temp_limit'])
    p.add_argument("--warmup-sec", type=int, default=DEFAULTS['warmup_sec'])
    p.add_argument("--collapse-drop-frac", type=float, default=DEFAULTS['collapse_drop_frac'])
    p.add_argument("--collapse-sustain-sec", type=int, default=DEFAULTS['collapse_sustain_sec'])
    p.add_argument("--load-gate-util-pct", type=float, default=DEFAULTS['load_gate_util_pct'])
    p.add_argument("--load-gate-a-load", type=float, default=DEFAULTS['load_gate_a_load'])
    p.add_argument("--smooth-n", type=int, default=DEFAULTS['smooth_n'])
    p.add_argument("--hwinfo-csv", type=str, default="", help="Optional HWiNFO CSV path for CPU power/temp or VRAM temp")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    monitor(args)
