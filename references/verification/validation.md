# Validation by purpose

Choose checks from material behavior, intended use, known uncertainty and user budget. Do not impose a universal circuit count, rigid chronology or all-feature probe catalog. Separate the following purposes even when one deck serves several:

| Purpose | Evidence needed |
|---|---|
| Calibration | Source-conditioned anchors/curves and stated fit objective/uncertainty |
| Independent verification | Unfitted points, independent relations or conditions that can reject an incorrect mechanism |
| Application behavior | Valid topology/stimulus, meaningful function and necessary quantitative requirements at the real ports |
| Numerical robustness | Resolving timestep/method, source/load/init or multiple-instance variations relevant to the claims |

Application checks may need numerical gain, error, timing, regulation, impedance or power criteria. They are not limited to “finite and did not crash.” Three circuits do not universally prove coverage. Cover materially different mechanisms/operating regimes; avoid repeated value variations with the same blind spot. Matching fit anchors alone is not independent verification.

## Large-signal application coverage

Nominal DC points, small-signal gain and a single load do not establish that a model is usable. For every claimed large-signal behavior, include at least one discriminating fixture. The categories below describe behaviors, not a universal circuit quota; select those that apply to the declared scope:

- **Feedback sign and closed-loop stability.** Unity-gain follower or closed-loop regulator under the actual load. An inverted input or error polarity can still produce a plausible open-loop polarity or nominal operating point.
- **Saturation and recovery.** Drive the model out of its linear region (comparator, input overdrive, startup, current limit, hard saturation) and verify the recovery time/state as well as the final value.
- **Protection and limits.** Output short or near-short, reverse/return conduction, off-state blocking and current limiting with finite sense elements.
- **Multi-instance interaction.** Parallel current sharing, cascaded stages and dual channels; verify subcircuit node scope and independent state.
- **Load and source extremes.** Open/light/nominal/heavy loads, capacitive/inductive loads and finite source impedance.
- **Startup and supply sequence.** Supply ramp, interruption, enable/disable and zero-output start. A converged `.op` root is not startup evidence.
- **Temperature and parameter corners.** At least the declared extremes; a room-temperature fit does not establish drift or corner stability.

Before changing a model because one of these fixtures fails, confirm the fixture itself is valid for the declared polarity, pin order, input common mode, load return and current-sense branch. Invalid-polarity or wrong-branch fixtures are a common source of false model failures.

Standalone metric names and printed tables must be parsed as described in [native execution semantics](../syntax/ngspice.md#analysis-execution-and-measurements); a missing or skipped analysis is not a pass.

Each material implemented behavior group needs an independent source-conditioned comparison. For a shared mechanism, also use a discriminating interaction or boundary that can reject mutually inconsistent headline parameters. Already agreed acceptance criteria remain binding; a smaller plan cannot silently delete them. Multiple stimuli in one deck still require their actual conditions and coverage to be stated; an unbounded sweep is not made small by calling it one circuit.

Split a source row when its sub-behaviors or conditions need different dispositions, or explicitly state the verified and deferred subsets. A DC rejection-ratio check does not cover its frequency response. Transient overshoot alone does not establish a general multi-state model's phase margin; a conversion is only a limited derivation when its simplified order and linear assumptions are independently supported. Verify loop gain and phase under the actual feedback/load conditions for a general phase-margin claim.

## Fixture and result contract

Before running, define actual top-level model/pin mapping, supply/reference/current returns, stimulus/state sequence, load, analysis, domain and units. Numeric tokens in node positions are node names, not voltages. Duplicated physical electrodes need their intended connectivity. A load-only fixture must still expose an observable; shorting all ports cannot demonstrate behavior.

Drive documented supply, control and signal inputs. Do not force an output or internal bias rail that the model is supposed to generate. Keep independent outputs on separate nodes with finite, appropriate loads; measure isolated outputs against their own local return. Intentional output-port injection for an impedance or port characterization is valid when the operating-point and injection contract explicitly require it; distinguish that measurement from accidentally clamping functional outputs.

For source/sink drive and swing, use finite physical load lines and inspect terminal current plus headroom relative to the appropriate signed rail. An ideal current demand outside compliance cannot establish a valid output limit. For impedance, establish DC bias and AC perturbation/returns; separate DC feedback used for bias from the open-loop AC excitation. Charge-port fixtures are defined in [charge measurement](../mechanisms/charge.md#mos-capacitance-fixtures).

Define expected values/bounds from sources or an independent derivation and select comparison projection (real, imaginary, magnitude, phase). Establish tolerances from source resolution, approximation and numerical error; never enlarge them to conceal failure. Numerical comparisons may use abs(actual-expected) <= atol+rtol*abs(expected), with finite operands and bounds. Windows/events must lie inside the actual returned domain; interpolation cannot invent missing coverage. Explicitly handle nested sweep segments instead of interpolating across resets.

Define timing thresholds at the observable named by the source: output voltage, supply current, reset release or another specified port. An internal enable crossing is not the measured turn-on/off time when output loading or downstream states intervene. When a settling or switching specification omits a material fixture value such as feedback resistance or capacitance, do not invent it and claim an identical-condition match. Keep the chosen fixture explicit, inspect sensitivity only where it resolves the uncertainty, and distinguish verified model behavior from the unresolved source-condition comparison.

Coordinate rounding must be smaller than the separation of independent requested conditions and the event/time resolution needed by the claim. Reject intended distinct points that collapse at numeric precision. Check actual start/end and maximum gaps as well as row count; a fixed absolute or coordinate-relative allowance must not conceal a shifted grid, missing endpoint or unresolved fast event.

Use exact allowed outcomes for Boolean/discrete-state oracles, not numeric tolerances that accept a different state. For lower/upper bounds, specify any endpoint allowance separately and keep computed errors/bounds finite. Typical fits and guaranteed limits remain distinct: a missed guaranteed limit requires a corner, scope or architecture decision, not silently moving a typical fit or treating a bound as its target.

Inspect the intervening response: equal initial/final outputs do not prove response to a stimulus. Intended oscillation, saturation, hysteresis or switching is not a failure merely for being nonconstant or nonlinear. Frequency-response claims need enough frequencies to resolve the claimed response; one low-frequency point does not establish bandwidth. A measurement requiring interpolation needs a supporting interval even when a one-point analysis itself is valid.

For stateful models, apply legal power/reset/pin sequences and choose duration/maxstep from the implemented conversion, propagation, oscillator or timeout scales. Busy/ready activity alone does not prove input data reached the output. Observe the required code/state/output event; missing its interval makes the check inconclusive. For event-table evaluation, verify the named node, complete table boundaries, legal state alphabet/strengths and ordered finite event times; do not turn a missing table into an empty passing trace.

When a specialized evaluator reads named scalar measurements from logs, require one complete finite value for each requested name in the intended analysis. Missing, duplicated, malformed or nonfinite measurements are evaluation failures, even if other analyses completed. Parsing or normalizing a result does not authenticate the underlying run; inspect its actual command and diagnostics.

A passive model's nominal point does not validate claimed ESR/ESL, resonance, loss, bias/temperature dependence or self-heating. Check a material dependence at at least two independent source-conditioned points, with additional points where a knee or model order requires them; a claimed dynamic state needs an interaction that distinguishes it from a static lookup. Use the [passive recipe](../recipes/passives.md) for family-specific conditions.

Execute the unchanged candidate with the selected engine and required modules/options. Use fresh output directories. Inspect actual outputs and diagnostics, not self-authored expected/actual JSON or hashes alone. The [runner](../execution/runner.md) derives supported metrics from native exported tables. Other native analyses can use a deterministic specialized evaluator with the same source/domain checks; unsupported helper metrics are not unsupported engine capabilities.

Acceptance combines successful execution, valid model loading, completed analysis/domain, required finite vectors and discriminating electrical metrics. A completion marker only proves command progress. A zero exit code, nonempty file, metric label or plausible trace is insufficient. Unknown model parameters, missing models/vectors, failed measurements and terminal solver errors need resolution.

Initial singular/gmin/source-step diagnostics can precede successful recovery. Separate recovery attempts from a terminal failure; inspect final completion, domain and values. Recovery is not by itself proof of correctness. The helper may return REVIEW_REQUIRED for diagnostics: resolve their significance using actual artifacts before concluding pass; do not suppress a warning class globally.

## Causal repair and stopping

Classify evidence, model architecture/equation/implementation, fixture, execution/configuration or evaluation causes before changing the model. Verify a responsive runtime with a minimal control only when a runtime hang/failure creates that uncertainty, not as routine installed-program testing. Bound subprocess runtime and stop only task-owned processes.

When a hang leaves execution uncertain, establish a responsive control and actual model loading before blaming the device or patching its parameters. Use only a bounded retry to resolve that runtime uncertainty. First inspect available raw values, source calculations, topology and analytic reconstruction; request another simulation only if they cannot distinguish the proposed cause, and say what new observation is needed.

Relevant repairs remain inside an authorized model-generation task. A separate user-requested read-only acceptance audit retains its scope. Preserve old candidates and failed outputs during repair, record the causal hypothesis and rerun dependent claims plus discriminating controls. A test defect does not justify regenerating a correct model. If a shared fixture invalidates earlier PASS results, reopen only dependent claims.

Choose a finite plan/stopping condition proportional to complexity and user budget. Repeated unexplained local patches trigger architecture review. Do not relabel a timeout, missing extraction, unrun check or unresolved defect as an ngspice/data ceiling. If the requested contract cannot be completed, state the concrete gap and its use impact.

Stop local parameter repair when required evidence is unresolved, the parameter is unidentifiable, independent behavior breaks, or causally different patches keep failing the same dependent regression. Reopen the evidence/architecture decision. At an agreed budget boundary stop automatic simulations/patching, preserve the active recovery state and complete independent authorized documentation; changing a candidate name does not reset the boundary.

## Completion and working evidence

Distinguish execution failure, evaluation failure, observed electrical failure and untested scope. PASS describes only checked behavior/conditions. Native mechanism probes are synthetic evidence, not chip qualification or proof of all families.

Complete required checks before declaring delivery complete. Report blockers and unfinished work separately; do not hide missing required validation behind a pending placeholder in an otherwise finished MD. For multi-device work, retain the complete membership/status denominator in the active summary and distinguish it from a selective retest subset. A subset must not overwrite the full campaign conclusion.

Reuse prior conclusions only for unchanged relevant sources, model/dependencies, fixture/conditions, oracle/tolerances and execution/evaluation semantics. If a historical MD survives without its raw results, treat it as a prior declaration, not a newly reproduced result. The absence of an optional archive alone does not justify a broad rerun; perform the checks required by the current claim and uncertainty.

Keep actual source calculations, outputs and failed attempts while making decisions. Default final delivery does not retain this chain: summarize real checked coverage and unresolved limits in one MD, then follow [final verification and cleanup](../delivery/files-and-cleanup.md). Never substitute “no permanent archive” for “no validation.”

Regression follows the changed dependency: electrical equations require affected electrical comparisons, parser changes require parser behavior checks, and workflow-only edits require a realistic construction walkthrough plus contradiction review. Unchanged scripts do not require the full historical simulator suite for a documentation release. Use deterministic local reduction for repeated metrics and inspect failures/conflicts in detail. When performance matters, reuse measured run time/point count; do not invent costs or run a separate benchmark without a discriminating need.
