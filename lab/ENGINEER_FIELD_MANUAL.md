# THERMAL-OPTIMIZATION COUPLING ANALYSIS
## Field Manual for Energy Systems Engineer

### PURPOSE
This procedure measures the coupling between computational optimization dynamics and thermal system response in AI training workloads. We quantify the energy balance between optimization instability (gradient norm spikes) and thermal efficiency degradation (heat transfer rate changes) to enable predictive thermal management.

**Why this matters:** Traditional thermal monitoring detects problems after they occur. This procedure predicts thermal instability 1 second before collapse, enabling proactive energy management.

---

### HEAT-TRANSFER ANALOGUE MAPPING

| RLE Term | Heat-Transfer Analogue | Description |
|----------|------------------------|-------------|
| η_util | System efficiency | Fraction of input power converted to useful work |
| η_stability | hA stability | Effective heat-transfer coefficient stability |
| A_load | ṁ or velocity term | Represents convective intensity / load acceleration |
| τ_sustain | τ_th | Thermal time constant (transient response) |

**Translation Note:** The RLE formulation maps directly to classical heat-transfer analysis. Use this table to connect the computational metrics to familiar thermal systems concepts.

---

### SYSTEM BOUNDARIES AND VARIABLES

#### Primary Measurements
| Variable | Symbol | Units | Sensor | Range |
|----------|--------|-------|--------|-------|
| Thermal Efficiency | RLE | dimensionless | Computed | 0.0 - 1.0 |
| Gradient Norm | ∇f | dimensionless | Training log | 0 - 50 |
| Heat Transfer Rate | Q̇ | W | Power sensor | 0 - 300W |
| Temperature Rise | ΔT | °C | Thermocouple | 0 - 50°C |
| Time Constant | τ | s | Computed | 1 - 10s |

#### Derived Quantities
| Variable | Symbol | Units | Calculation |
|----------|--------|-------|-------------|
| Thermal Time Constant | τ_th | s | ΔT / (dT/dt) |
| Power Efficiency | η_p | dimensionless | Q̇_useful / Q̇_total |
| Optimization Instability | σ_opt | dimensionless | std(∇f) / mean(∇f) |
| Thermal Lag | t_lag | s | Cross-correlation peak |

---

### ENERGY BALANCE EQUATIONS

#### Primary Conservation Equation
```
RLE = (η_util × η_stability) / (A_load × (1 + 1/τ_sustain))
```

Where:
- η_util = utilization efficiency (dimensionless)
- η_stability = thermal stability factor (dimensionless)  
- A_load = load acceleration (dimensionless)
- τ_sustain = thermal sustainment time (s)

#### Heat Transfer Rate
```
Q̇ = hA × ΔT + ṁ × cp × dT/dt
```

Where:
- hA = heat transfer coefficient × area (W/°C)
- ΔT = temperature difference (°C)
- ṁ = mass flow rate (kg/s)
- cp = specific heat capacity (J/kg·°C)

#### Optimization-Thermal Coupling
```
dRLE/dt = -k × ∇f(t - t_lag)
```

Where:
- k = coupling coefficient (s⁻¹)
- t_lag = thermal response lag (s)

---

### PROCEDURE

#### Step 1: System Initialization
1. Verify all sensors: GPU temp, power, utilization
2. Initialize training workload: DistilGPT-2, 200 steps
3. Set sampling rate: 1 Hz
4. Record ambient conditions: T_ambient = 21°C

#### Step 2: Synchronized Data Collection
1. Start thermal monitoring: `hardware_monitor_v2.py --mode both --sample-hz 1`
2. Start optimization logging: `extended_training_with_sync.py`
3. Run for 90 seconds (steady-state thermal response)
4. Stop both processes simultaneously

#### Step 3: Data Alignment
1. Align timestamps using shared clock reference
2. Merge thermal and optimization data streams
3. Verify alignment tolerance: ±2 seconds
4. Record aligned sample count: N_samples

#### Step 4: Correlation Analysis
1. Calculate cross-correlation: RLE vs ∇f
2. Perform lag analysis: ±3 second window
3. Identify peak correlation: r_peak at t_lag
4. Determine causal order: ∇f → RLE or RLE → ∇f

#### Step 5: Energy Balance Validation
1. Check thermal time constant: τ_th = ΔT / (dT/dt)
2. Verify heat transfer rate: Q̇ = P_measured
3. Calculate efficiency drop: ΔRLE = RLE_max - RLE_min
4. Confirm energy conservation: Q̇_in = Q̇_out + Q̇_stored

---

### DATA SHEET TEMPLATE

#### Session Information
```
Session ID: _______________
Date: _______________
Duration: _______________ s
Ambient Temp: _______________ °C
Model: _______________
```

#### Thermal Measurements
```
Time (s) | T_GPU (°C) | P (W) | RLE | Collapse | Q̇ (W)
---------|------------|-------|-----|----------|-------
0.0      |            |       |     |          |
1.0      |            |       |     |          |
2.0      |            |       |     |          |
...      |            |       |     |          |
```

#### Optimization Measurements
```
Time (s) | ∇f | Loss | LR | Epoch | Step
---------|----|----- |----|-------|-----
0.0      |    |      |    |       |
1.0      |    |      |    |       |
2.0      |    |      |    |       |
...      |    |      |    |       |
```

#### Correlation Results
```
Metric | Value | Units | Interpretation
-------|-------|-------|---------------
r_peak |       |       | Peak correlation coefficient
t_lag  |       | s     | Thermal response lag
τ_th   |       | s     | Thermal time constant
η_p    |       |       | Power efficiency
```

---

### INTERPRETATION GUIDELINES

#### Thermal Response Analysis
- **If t_lag < 0**: ∇f spikes precede RLE drops → Optimization instability causes thermal degradation
- **If t_lag > 0**: RLE drops precede ∇f spikes → Thermal throttling affects optimization
- **If t_lag ≈ 0**: Simultaneous coupling → Strong thermal-optimization coupling

#### Energy Efficiency Assessment
- **If r_peak > 0.5**: Strong thermal-optimization coupling → Predictive capability confirmed
- **If 0.3 < r_peak < 0.5**: Moderate coupling → Requires controlled conditions
- **If r_peak < 0.3**: Weak coupling → Insufficient thermal stress or measurement issues

#### Thermal Time Constant
- **If τ_th < 2s**: Fast thermal response → High thermal coupling
- **If 2s < τ_th < 5s**: Normal thermal response → Standard thermal behavior
- **If τ_th > 5s**: Slow thermal response → Thermal isolation or large thermal mass

#### Power Efficiency
- **If η_p > 0.8**: High efficiency → Optimal thermal management
- **If 0.6 < η_p < 0.8**: Moderate efficiency → Room for improvement
- **If η_p < 0.6**: Low efficiency → Thermal management issues

---

### TROUBLESHOOTING

#### Common Issues
1. **No correlation detected**: Check timestamp alignment, verify thermal stress
2. **Reverse causality**: Verify sensor calibration, check for thermal throttling
3. **High variability**: Ensure controlled conditions, check for external heat sources
4. **Missing data**: Verify sensor connections, check sampling rate

#### Quality Checks
1. **Energy conservation**: Q̇_in ≈ Q̇_out + Q̇_stored
2. **Thermal response**: dT/dt should follow power input with time constant τ_th
3. **Optimization stability**: ∇f should show training convergence pattern
4. **Data alignment**: Timestamp differences < 2 seconds

---

### EXPECTED RESULTS

#### Successful Measurement
- **Peak correlation**: |r_peak| > 0.3
- **Thermal lag**: t_lag = -1 ± 0.5 seconds
- **Causal order**: ∇f → RLE (optimization instability causes thermal degradation)
- **Energy balance**: Conservation equation satisfied within 5%

#### Calibration Values
- **Thermal time constant**: τ_th = 3 ± 1 seconds
- **Power efficiency**: η_p = 0.7 ± 0.1
- **Coupling coefficient**: k = 0.1 ± 0.05 s⁻¹
- **Response lag**: t_lag = -1 ± 0.5 seconds

---

### COMMAND REFERENCE

#### Quick Start
```bash
# Single session analysis
python run_joint_session.py --model distilgpt2 --duration 90 --output results/

# Reproducibility analysis  
python analysis/reproducibility_analysis.py

# Calibration dataset
python calibration_dataset.py
```

#### Manual Analysis
```bash
# Analyze specific session
python analyze_session.py --rle-file data.csv --train-file log.json --output-dir results/
```

---

### NOTES FOR ENGINEER

This procedure measures the **energy balance between computational optimization and thermal system response**. The key insight is that optimization instability (high gradient norms) creates thermal stress that degrades efficiency before temperature limits are reached.

**Practical application**: Use this to implement predictive thermal management in AI training systems. When gradient norms spike, reduce workload intensity 1 second before thermal collapse occurs.

**Validation**: Run multiple sessions under identical conditions to establish reproducibility. The coupling should be consistent within ±20% across sessions.

**Extension**: This procedure can be adapted for any thermal system with computational workload coupling (mobile devices, edge computing, data centers).
