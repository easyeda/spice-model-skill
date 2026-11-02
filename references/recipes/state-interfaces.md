# Stateful, mixed-signal and interface devices

Build a task-specific state/port architecture from actual source definitions. This is not a universal silicon schematic.

For clocked or serially controlled devices, drive register/conversion/enable/commit state from the physical clock, select, reset and control pins and specified active edges. Preserve frame boundaries, incomplete-frame behavior, deselection/output release and asynchronous controls when defined. Absolute-time schedules, preselected words and always-on cores cannot replace a materially specified protocol.

Choose native behavioral, XSPICE, code-model or OSDI routes according to state complexity and actual build support. Validate a complete transaction and deselected state, then vary start time, clock period and relevant data to reject time-scheduled or fixed-code substitutes. If the interface cannot be implemented, identify narrower scope and its consequences; do not claim a general device.

For ADC/DAC transfer, protocol success is independent of static accuracy. Extract reference/supply/calibration-conditioned offset, gain, transfer thresholds and INL/DNL where supported. A coarse trace may support broad INL shape but not code-level errors, randomness or population statistics. Use [source interpretation](../sources/evidence.md) for extraction limits and [noise](../mechanisms/noise.md) for stochastic claims.

## Electrical boundary of digital state

- Derive input domain from published VIH/VIL and references. A source-unspecified transition band needs an explicit threshold assumption, not an unrelated supply midpoint. An adc_bridge's UNKNOWN interval is not hysteresis.
- Static model-card thresholds cannot refer directly to dynamic supply-node voltage. Normalize the input to the local supply domain before a static bridge threshold where appropriate; handle zero supply without division by zero.
- Digital Z is not automatically an analog high-impedance pin. A voltage-only dac_bridge does not prove tristate release. Use a drive-strength-aware bridge or finite-conductance output; check disabled current/voltage with pull-up and pull-down.
- Open-drain/collector means release or sink, not active high drive. The fixture needs an external pull-up for a defined high state.
- Account separately for event delay and analog-port delay from threshold, edge, impedance and load. Do not count end-to-end source delay twice.
- A fixed bridge voltage does not implement supply pins, load-current returns or powered-down impedance. Define supply dependence and UNKNOWN-state policy.

For comparator hysteresis, low state persists until the upper threshold is crossed, and high state until input falls below the lower threshold. Derive both thresholds from the same state and verify rising/falling sequences. Hysteresis magnitude alone cannot establish correct feedback polarity.

If a resistive-load transition stalls but the sourced capacitive-load fixture succeeds, diagnose missing output storage rather than assuming general stability. A justified effective capacitance needs provenance or an explicit assumption and renewed timing/edge checks. A successful capacitive fixture does not qualify resistive-only operation.
