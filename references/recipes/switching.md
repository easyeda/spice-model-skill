# Switching-power, driver, and oscillator synthesis

These classes need an explicit task contract before implementation. Choose switching, averaged, event/state, or hybrid architecture from the observable that matters. An averaged converter can support regulation and envelope behavior within its conduction-mode assumptions; it cannot claim ripple, switching-node stress, dead time, switching loss, subharmonic behavior, or cycle-by-cycle protection. A switching model is justified only when those observables are sourced and required.

## Converter and driver construction

For buck, boost and buck-boost devices, define control law, switching frequency/timing, conduction mode, current sensing/limit, startup/soft-start, compensation, dropout/duty limits, enable and fault state before coding. Include finite losses and parasitic paths only from evidence or disclosed circuit choices. Do not add arbitrary damping to make convergence appear successful.

When the declared use spans distinct power-transfer regimes, validate each materially claimed regime with a representative circuit; for example, a buck-boost model may need separate buck, boost and near-crossover circuits. Several loads within one regime do not establish behavior in another. For an averaged representation, assess regulation/envelope behavior and steady-state power or energy closure at the relevant ports; do not use switching ripple or timing as acceptance criteria unless the model explicitly represents them.

For gate, motor and LED drivers, define input thresholds, actual output topology, finite source/sink behavior, propagation and dead time, supply/current returns, disabled/power-off impedance, bootstrap or charge-pump state, UVLO and fault/retry behavior where supported. Validate source and sink transitions with realistic loads and include the supply/bootstrap interaction when it is material.

## Closed-loop behavioral regulators and PWM controllers

For an averaged regulator or a controller macromodel, verify the loop's sign and reachability, not only its nominal regulation point:

- **Error-sign reachability.** An output below its reference must increase drive. Start from a discharged output or a documented supply ramp, never only from a converged `.op` root. A model that regulates only when the DC solver is handed the correct root is incomplete.
- **Reference definition.** Derive the reference relation from the datasheet definition and the actual pin semantics. For an adjustable regulator the reference may be defined between output and adjust rather than from adjust to ground; check the closed-loop equation with a known divider and the specified adjust-pin current.
- **Controller completeness.** A PWM controller needs the reference, error amplifier, oscillator/ramp and comparator, plus the current-limit or blanking mechanism required by the claimed closed-loop behavior. An open compensation/feedback path or a comparator without a reference is not a controller.
- **Protection as a load line.** Implement current limit and anti-overvoltage/return clamps as finite causal relations in an averaged model. Ideal diodes or unbounded pass-current sources do not establish transient robustness; measure short-circuit current, load-step recovery and startup overshoot at the actual ports.
- **Regime coverage.** If the declared use includes startup, load step, line step, short circuit and temperature corners, use separate fixtures for those regimes. One nominal load does not cover loop sign, headroom, protection or corner stability.

Nominal output voltage alone is not evidence of a usable closed loop.

## Startup and operating point

A self-oscillating or hysteretic switching system may have no unique behaviorally meaningful DC operating point. Do not use `.op` or `.dc` convergence as validation of oscillation, startup or steady switching. State whether transient initialization comes from a physically meaningful operating point or from documented initial state/energy.

Use UIC only when the initial capacitor voltages, inductor currents and control states are explicit parts of the model/fixture contract. UIC is not a workaround for missing DC paths, floating nodes, undefined state or an invalid topology. Retain startup time, final periodic or regulated condition, and the complete interval needed to distinguish startup failure from slow startup.

## Integration method and timestep

Predeclare maximum timestep and sampled metrics from the highest relevant switching or state-transition rate. Trapezoidal integration can expose numerical ringing; Gear can suppress ringing and also add numerical damping. Change method only as a diagnostic tied to an observed waveform.

When a conclusion depends on ringing, damping, loss, peak stress or periodic stability, compare trapezoidal and Gear results at the same bounded metrics and adequate timestep. Agreement within a predeclared tolerance supports numerical robustness. Material disagreement remains `NUMERICAL_UNRESOLVED`; do not select whichever method produces the preferred waveform or hide the method in a default option.

## Oscillator, PLL and timer

Define phase/frequency state, amplitude limiting, startup perturbation or initial state, control transfer, duty-cycle mechanism, supply dependence and lock/reset behavior. Add jitter or phase-noise behavior only with source evidence and a defined stochastic contract. Frequency from a static algebraic source does not establish startup, capture, lock, duty cycle or perturbation response.

Validate startup, one steady oscillation/locking metric, supply/control dependence and every material state transition. Use time-window and cycle-count criteria that can reject missing startup, false lock, skipped pulses or nonperiodic drift. A solver completion marker is not an oscillator oracle.

Use the shared [charge/flux](../mechanisms/charge.md), [noise](../mechanisms/noise.md) and [temperature/electrothermal](../mechanisms/temperature.md) recipes for these mechanisms and implicit native behavior. Do not duplicate their constitutive rules in a family-specific patch.
