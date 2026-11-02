# Coupled architecture before implementation

Use [source interpretation](../sources/evidence.md) to establish material observables and conditions. In one temporary [construction record](../../assets/model-blueprint.md), map:

    observable + condition -> block/ports -> constitutive/state equation
    -> parameter derivation -> interacting observables -> unresolved gap

Choose the simplest representation that preserves all source-supported behavior material to intended use. A one-pole ideal-output op-amp is insufficient if load current, swing and loop dynamics matter. A transistor reconstruction is unjustified when process parameters are unidentifiable. Unidentified internal parameters do not excuse omission of identifiable external behavior.

For a general-purpose model request, do not preselect static-only scope. Review the source-supported dynamic and coupled behaviors first. Keep a performance budget and identify cost drivers (fast states, stiff time constants, event rate or expensive expressions); a budget constrains work, not the truth of the claimed scope.

## Ports, states and equations

For each block define ordered terminals, sign convention, local reference, DC relation/equilibrium, small-signal derivative, dynamic state/initialization, mode transitions and current/energy return. Explain whether each port/state return comes from model, application or fixture. AC and DC closure can differ; excitation alone does not supply a return.

Physical pads/tabs representing one electrode need the intended common net unless the source distinguishes roles. Do not repurpose or ground an extra terminal for fixture convenience. Preserve independent state across channels/instances; share only source-supported interactions. Avoid variable supply/reference ports named as global nodes.

Derive coupled parameters together: gain/poles/gm, load/swing/output impedance, slew/current/capacitance, delay/state/output loading. Sum **all** connected elements: a resistor already implementing a loss term must not be repeated inside a B source; a downstream passive pole loads upstream state unless buffered or included in the derivation. Check dimensions, signs, endpoints, limits, conservation and causality before simulation.

Reusable [charge](../mechanisms/charge.md), [noise](../mechanisms/noise.md) and [temperature](../mechanisms/temperature.md) rules own their constitutive and implicit-native behavior. Choose family structure from [recipes](../recipes/index.md), exact grammar from [syntax](../syntax/ngspice.md), and numerical regularization from [numerical diagnosis](../verification/numerical.md).

## Representation and vendor adaptation

Compare relevant native primitives/compact models, vendor subcircuits, behavioral charge/state equations, XSPICE and custom/OSDI mechanisms. Do not mandate every option or prefer vendor text without analysis. Inspect license, pin ordering, dialect, supported analyses, hidden references and state. Separate syntax translation from changed equations. Fix a problematic representation without silently removing its behavior; recurring structural failure can justify a fresh coherent architecture.

Use exact linear E/F/G/H relations where they express the intended law. Do not inherit a vendor model's global ground, unexplained stiff state or compatibility workaround without checking its role in the local-port contract. Illustrative equation/netlist fragments are not executable candidates until their definitions, parameters, states and ports are complete.

Before the first complete candidate, classify every material behavior as implemented/planned, evidence extraction pending, implementation pending, explicitly excluded by user, or blocked by a documented gap. Include real package wrapper, limits, initialization and supported modes together. A list of future tests is not an architecture. Experiments may resolve a specific uncertainty, but omitted material blocks must not be added opportunistically just to pass successive fixtures.

Preserve the first complete candidate before calibration/fitting while work is active. Record what would reopen the architecture decision: newly extracted material evidence, incompatible source conditions, an unidentifiable parameter, a representation limit, or failed independent coupled behavior. A reviewed design and its NOT_RUN plan are not implemented or verified results.

When public evidence conflicts or does not identify a needed mechanism, record reviewed sources, alternative representations, retained coupling, missing observable and circuit impact. A missing core keeps the requested model incomplete unless the user accepts narrower scope. Disclosing an assumption is not permission to invent that core.

Distinguish construction parameters from identified device parameters. Analyst-selected smoothing times, loop gains or regularization values remain ASSUMED even when they make a candidate stable or help it match one operating point; neither result identifies silicon compensation. State their role and effect on the supported envelope in the MD. Where a material prediction depends on such a choice, use an independently sourced dynamic anchor or a targeted sensitivity check to expose that dependence, and retain the resulting uncertainty. A source-derived fit may be reported as DERIVED when its data, equations and identifiability support that claim; a disclosed free parameter alone cannot establish source-limited fidelity.

## Corrections and reuse

Each correction has a cause, affected equations/parameters and dependent observables. Review every claim governed by the changed mechanism. Preserve the failed candidate/output during repair; reject patches that repeatedly break independent behavior. Use bounded, hypothesis-driven work under [validation](../verification/validation.md), not a universal iteration quota or new permission gate.

Recipe reuse requires matching topology, modes, operating envelope, evidence and runtime assumptions; a common name prefix is insufficient. Re-extract device-specific values. Reusing architecture never transfers another device's PASS.

For composed circuits, begin with topology/values, constituent models and port contract; derive coupled bias, impedance, resonance, gain, loading, energy and swing. Constituent facts keep provenance, user values are scenario inputs, and circuit performance is DERIVED. No separate circuit datasheet is required.

**Discriminating check:** perturb one shared parameter or load and predict which independent observables must change. A model made of disconnected headline-value patches cannot satisfy that relationship.
