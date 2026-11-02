---
name: spice-chip-modeling
description: Build, audit, or validate native ngspice models from datasheets and public technical sources for passive components, semiconductors, ICs, and composed circuits.
metadata:
  short-description: Evidence-based native ngspice model generation
  version: "1.1.2"
---

# Native ngspice model generation

Build the highest useful external fidelity supported by authentic sources, intended circuit use, and native ngspice. Derive observable behavior, coupled equations, states and ports before implementing a complete candidate. More internal detail does not establish more fidelity. This package is **v1.1.2**; resolve all resources relative to it.

Use the conversation's scope and existing authorization. A model-generation request includes relevant source extraction, engine setup, meaningful verification, causal repairs and cleanup. Audit-only or design-only requests stay within those bounds. Ask for a materially missing requirement; do not ask again for work already authorized.

## Workflow and reference ownership

1. Establish exact part/package/pins, intended use, source revision and conditions using [source interpretation](references/sources/evidence.md). Existing but unextracted evidence is pending work, not unavailable information.
2. Map each material observable to its coupled equation, state, parameter derivation and uncertainty using [architecture](references/modeling/architecture.md). Select the applicable [family recipe](references/recipes/index.md). Use [charge](references/mechanisms/charge.md), [noise](references/mechanisms/noise.md), and [temperature/electrothermal](references/mechanisms/temperature.md) when those mechanisms or their implicit native behavior matter.
3. Reuse a suitable native engine or [obtain the latest official stable release](references/execution/provisioning.md) if absent. Implement the complete declared scope using [native syntax](references/syntax/ngspice.md). When representation is uncertain, consult [native capabilities](references/execution/capabilities.md); a helper's limits do not limit the engine.
4. Verify calibration, independent behavior, application behavior and relevant numerical robustness under the [validation contract](references/verification/validation.md). Application verification includes the applicable [large-signal usability checks](references/verification/validation.md#large-signal-application-coverage): feedback sign, saturation/recovery, protection and limits, startup, load/source extremes, multi-instance interaction and temperature corners. Use the [native runner](references/execution/runner.md) or direct native execution with deterministic evaluation. Fix confirmed causes within the authorized task and rerun affected checks. Consult [numerical diagnosis](references/verification/numerical.md) as needed.
5. [Deliver necessary model-use files and one concise MD, then clean task-owned intermediates](references/delivery/files-and-cleanup.md). Load actual final bytes with final dependency paths before cleanup. Preserve unresolved repair state only while needed. Do not deliver validation chains by default.

Keep one temporary [construction record](assets/model-blueprint.md) when useful; do not create duplicate evidence/design/report documents. Read only references relevant to the selected work.

## Modeling boundaries

- Distinguish source facts, derivations, assumptions and unresolved evidence. Bounds, unknown signs and typical curves do not define population distributions or hidden silicon structure.
- Preserve physical pin order, local references, loading, current/power returns and independent states. Account for all connected elements when deriving gain, loss, delay, charge and energy.
- Never reduce claimed fidelity or loosen criteria merely to pass a fixture. Missing extraction, missing implementation, unrun validation and an engine limitation are different outcomes.
- Native SPICE, behavioral sources, XSPICE, custom code models and Verilog-A/OSDI are design routes when appropriate to the actual build. No device-prefix whitelist applies.
- Nominal DC/small-signal agreement and a single-load sweep do not establish closed-loop or large-signal usability. Accept a model for its declared use only after the applicable large-signal invariants are exercised.
- A zero exit code, completion marker or plausible plot is insufficient. Numerical claims must come from actual engine output and independently justified expectations. State only the coverage actually verified.

For an authorized skill update, use [rule placement and promotion](references/maintenance/rule-placement.md). Detailed rules have one owner; add cross-references rather than copies.
