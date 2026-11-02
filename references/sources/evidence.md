# Source interpretation

Obtain and read authentic technical sources for the exact manufacturer, part, package and revision. Reuse verified originals. Search snippets, memory and related-part values cannot replace this device's sources. A URL, PDF suffix, HTTP success or hash alone does not prove identity or authenticity. Inspect document identity and relevant pinouts, tables, curves and footnotes; visually resolve merged columns, axes, active-low symbols and diagram viewpoints.

Maintain one temporary source-to-behavior table in the [construction record](../../assets/model-blueprint.md). Each row identifies observable, source class, document number/revision/page/figure, source location or URL, units/statistic/conditions, extracted values or relation, extraction uncertainty and evidence state. Record which relevant pages/sections were actually checked. Detailed acquisition inventories are optional. Do not create a second table that repeats the architecture mapping.

| Class | Meaning |
|---|---|
| DATASHEET / REFERENCE_MANUAL / APPLICATION_NOTE / MANUFACTURER_MODEL | Identified source, exact conditions and scope |
| DERIVED | Equation plus upstream source rows and assumptions |
| ASSUMED | Disclosed engineering choice; not a missing vendor fact |
| UNAVAILABLE | Needed information still absent after relevant source review |
| Scenario input | User topology, values, load and stimulus; separate from device provenance |

## Interpretation rules

- MIN/TYP/MAX, absolute maxima, test conditions and typical curves are different evidence. A midpoint of limits is not TYP; an absolute maximum is not a protection threshold or operating law. Bounds/unknown signs do not imply statistical distributions, correlations or a signed typical value. A guaranteed threshold interval does not identify an exact switching threshold or hysteresis. Preserve printed signed statistics: a negative-current MAX column need not be an algebraic upper bound.
- For missing material behavior, check relevant manufacturer manuals, notes or model sources. A distributor/mirror copy needs identity/completeness checking. Report unresolved source authenticity rather than presenting a model as manufacturer-backed.
- Available but unextracted curves are EVIDENCE_PENDING, not UNAVAILABLE. Name the source anchor, parameter/decision it must resolve, and smallest extraction needed. Extract what changes material architecture before making a source-limited conclusion. Missing plot precision alone is not DATASHEET_LIMITED. Implementation pending and validation not run are also distinct.
- Curve extraction keeps axes, temperature/bias/load, trace thickness/pixel uncertainty and interpolation/extrapolation policy. A plot across thousands of ADC codes cannot resolve per-code DNL. Do not claim more precision than the pixels support.
- Derivation or a constrained fit can identify external behavior without uniquely identifying internal process parameters. Keep source points, fit objective, conditions, uncertainty, physical constraints and upstream equations while working. Derivation dependencies must not be circular; never fit to the candidate's own outputs. Fitted anchors are not independent validation.
- Compare conflicting definitions/conditions before reconciling tables, curves, revisions or model equations. Preserve the original sources unchanged. Do not average incompatible evidence or invent compensation terms. Document each conflicting anchor, the proposed interpretation and unresolved effect on intended use. Related-part values do not become this part's evidence merely by labeling them.
- In a shared family datasheet, resolve the variant named by each table heading, figure caption, trace and footnote before using its values. A sibling's load-transient plot does not identify the selected variant's loop response merely because both appear in the same PDF. Transfer a relation only when the source establishes that it applies to the selected variant; otherwise keep it as comparison evidence and mark the target behavior unresolved. Reconstruct the exact variant and conditions from the cited anchor as the discriminating check.

Source class identifies provenance, not confidence. Unresolved identity, authenticity or completeness remains unresolved even if a file has a hash; pause source-dependent modeling until it is resolved, obtaining missing source information from the user when necessary. Read pinout/conditions for the port contract, functional diagrams for observable block coupling, DC tables for static anchors, AC/transient specifications for states, typical curves for dependence, and vendor models for a possible representation. Stop unrelated source expansion when the remaining details cannot change a material architecture or acceptance decision.

Keep an unknown sign or bounded quantity active as a parameter/bound rather than silently choosing a signed typical value. In particular, a symmetric plus/minus typical bound does not identify one polarity. Engineering assumptions may define a disclosed approximation or scenario; they cannot manufacture a missing material device fact.

**Discriminating check:** trace an implemented parameter back to the actual source row/curve and reconstruct its units, sign/statistic and condition. Try a plausible misreading (wrong temperature, column, pin view or typical/bound interpretation); the source note must distinguish it.

Use per-behavior coverage: **observable x conditions x error/bounds x evidence/implementation/verification status**. Noise, thermal, protocol, DC and dynamic fidelity are independent axes; a scalar L0-L5 ladder cannot summarize them. Limits can arise from evidence, a build, architecture or uncompleted work; name the actual cause. Source evidence does not become stronger because the model runs.
