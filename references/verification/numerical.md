# Numerical Stability and Failure Analysis

Numerical stability is a design property. Treat convergence messages as evidence about an equation or topology, not as permission to broadly weaken simulator tolerances.

Use the architecture questions while deriving equations, before simulation. Apply the [bounded correction policy](validation.md) during diagnosis: existing waveforms, dimensions, DC equations and linearization come before new experiments. The list below is not an automatic sweep plan.

## Architecture review before tuning options

For every nonlinear or stateful model, explicitly answer:

- Does every electrical node have an intentional DC path? Off states need a documented leakage or resistance when physically appropriate.
- Does a source impose an ideal voltage/current conflict with another ideal element? Give output stages finite impedance or use a valid topology.
- Are all B-source expressions finite across startup, power-off, reverse-bias, and parameter limits? Guard denominators and domain-limited functions.
- Does every discontinuity have a physically defensible transition, hysteresis, RC state, or event mechanism? Smooth only enough to model an omitted physical transition; record the timing impact.
- Are hidden states initialized from a credible powered/unpowered condition? Do not require arbitrary user `.ic` values to make normal startup work.
- Are time constants, impedances, and state gains scaled to avoid extreme stiffness without erasing a required behavior?
- Is a physical pin accidentally treated as a global node? In ngspice `0` and `GND` are global references; do not name a variable negative-rail formal subcircuit port `GND`.

- A behavioral output or protection stage made of an ideal voltage source, a small series resistance and an exponential clamp has no finite short-circuit current: the clamp either fails to hold the node or forces vanishing timesteps. Give the stage a finite source/sink current limit, or a documented linear clamp with a stated slope and overlap, and verify short and overdrive.
- An averaged regulator whose pass element only sources current when the error amplifier output has the correct sign can have a valid DC root that is unreachable from a discharged output. Verify startup from the documented initial state; do not treat the solver's converged operating point as evidence of reachability.
- An extracted primitive card may add quasi-saturation or high-current keywords that the target build implements as a stiff region. Run a saturated-switch transient as well as an active-region DC point. If the card cannot converge there, classify the limitation and consider a supported simplification that retains the claimed active-region behavior instead of hiding it behind global tolerances.

For each smoothed branch, record the transition variable, endpoints, width, limiting values, and the one-sided first derivative. The relation must be finite and continuous; when charge, Newton linearization, or a small-signal claim depends on the derivative, the derivative must also be continuous unless a source-supported event mechanism is explicit. A voltage-driven fixture can hide a derivative discontinuity that a current-driven charge fixture exposes as a timestep failure.

A numerical leakage, shunt, bleeder, damping path, or lead-parasitic regularizer is `ASSUMED` unless sourced. Calculate its current, bias shift, and stored-energy or impedance effect at every declared off-state and source condition. A gate-to-drain numerical path must not form a divider that changes the initial floating-gate voltage; numerical paths must be negligible relative to the source leakage and declared observable accuracy.

## Endpoint derivatives and state initialization

A finite expression value does not imply a finite Jacobian. Noise weights such as sqrt(w) and sqrt(1-w) have singular derivatives at endpoint biases even when the instantaneous noise voltage is zero. For bias-dependent weights, use bounded endpoint branches or a differentiable interior guard, preserve the intended PSD at both endpoints, and quantify any changed transition region. A quiet transient at a nonzero local rail and the affected noise spectrum discriminate this defect from an incorrect physical noise level; do not copy a device-specific epsilon into every model.

State coefficients can be zero at a Newton initial guess even when the final legal supply makes them positive. Guard all relevant denominators and coefficient ratios consistently, including compensating numerators, without changing the legal-region transfer. Derive the DC equilibrium explicitly. A hard completion branch that makes both state drive and its DC derivative vanish can leave a timer or progress state unconstrained; prefer a uniquely defined equilibrium while retaining the observable event time. Check the actual port timing after the change.

A hard numeric power-enable branch can disconnect a physical drive or compensation path during a supply ramp. Use a consistent, bounded transition for coupled drive, state and current-return equations where needed; distinguish this numerical treatment from an evidenced UVLO or physical protection threshold. Compare the full ramp/recovery domain and the unchanged powered behavior. A solver recovery trace or a short quiet run does not establish the required steady-state root: check the final state against its DC equation before treating initialization as solved.

## Remediation order

1. Correct invalid topology, source orientation, pin mapping, state polarity, or missing output/load path.
2. Replace an arbitrary hard branch with a source-labelled physical transition, hysteresis, or state equation.
3. Add a documented finite output resistance, leakage, parasitic capacitance, or damping only when physically plausible and quantify its effect.
4. Reduce model order or choose an average/event architecture if detail has no supported observable benefit.
5. Use analysis-local solver controls only with documented evidence of why the model cannot be made stable otherwise. Never make a global-option workaround the default proof of a model.

## Robustness matrix

Select material boundaries from the MAD and map them to claims. Document the selected scope once; do not create separate exclusion paperwork for every irrelevant cell.

| Boundary | Test objective |
|---|---|
| Ideal / finite source impedance | expose ideal-source assumptions and input current interaction |
| Slow / fast supply ramp; interruption | verify initialization, UVLO, and recovery |
| Open / light / nominal / heavy / near-short load | verify output topology, current and fault limits |
| Resistive / capacitive / inductive load | expose damping, loop, and energy-storage behavior |
| Threshold / overdrive / feedback condition | expose discontinuities, metastable architecture, and loop interaction |
| Startup / shutdown / enable-disable | verify state release and non-powered behavior |
| Multiple / cascaded instances | expose global state, node-name, and contention bugs |
| Long run / resolving step / practical larger step | distinguish valid dynamics from step-size overfit and cost blow-up |

When a switched output model claims operation without external capacitance, include an applicable resistive-load transition check in the planned batch. Internal damping needs a labelled rationale and a timing-impact bound. Use a second resolving timestep when step sensitivity affects the conclusion, not as a ritual for every waveform.

## Failure taxonomy

Classify before correcting. A failure can have one primary category and supporting evidence.

`DATASHEET_INFORMATION_INSUFFICIENT`, `PARAMETER_EXTRACTION_ERROR`, `DEVICE_CLASSIFICATION_ERROR`, `MODEL_ARCHITECTURE_ERROR`, `MODEL_PARAMETER_ERROR`, `SIGN_OR_POLARITY_ERROR`, `NGSPICE_SYNTAX_ERROR`, `DC_CONVERGENCE_ERROR`, `TRANSIENT_CONVERGENCE_ERROR`, `NUMERICAL_INSTABILITY`, `INITIALIZATION_ERROR`, `BEHAVIOR_MISMATCH`, `MODEL_OVERFIT`, `PERFORMANCE_EXCESSIVE`, `NGSPICE_LIMITATION`, `FIXTURE_TOPOLOGY_ERROR`, `ANALYSIS_EXECUTION_ERROR`, `MEASUREMENT_PARSING_ERROR`.

Failure record fields: device/model revision, native ngspice build, optional runtime identifier, minimal reproducer, native command sequence, expected observation, actual result, log excerpt, primary category, root-cause evidence, correction, regression test, and whether the Skill rule changed. Three unrelated patches to one architecture trigger a MAD review.
