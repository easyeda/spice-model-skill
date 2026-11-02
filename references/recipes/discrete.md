# Discrete semiconductor synthesis

Use this recipe with the evidence matrix and mechanism rules in [charge](../mechanisms/charge.md), [noise](../mechanisms/noise.md), and [temperature](../mechanisms/temperature.md). A manufacturer model is strong input only after its license, pin order, supported ngspice syntax, material mechanisms and operating range are inspected. Never claim a dynamic or survival behavior from a static model card.

## MOSFET

1. Fix polarity, pin order, package variants and intended switching or linear use. Separate absolute maxima from operating and test conditions.
2. Build one joint static contract from transfer/output curves, threshold definition, body-diode I-V and every claimed `RDS(on)` condition. Confirm the channel law can reproduce the current and voltages used by any later gate-charge fixture.
3. If only local small-signal use is required, implement source-conditioned terminal capacitances over the declared bias range. If switching is material, construct charge-consistent terminal behavior and test `Qg`, Miller interval, `VGS`, `VDS`, `ID` and gate current together. Do not replace a trajectory-defined charge curve with independent constant capacitors.
4. Add reverse recovery, avalanche, electrothermal state, SOA or damage behavior only when the source provides enough time-, energy-, temperature- and condition-dependent evidence. Otherwise exclude it explicitly.
5. Validate static anchors, isolated port capacitance or charge derivatives, and one representative coupled switching trajectory when claimed.

VDMOS labels such as `mfg`, `Vds`, `Ron` and `Qg` are informational metadata, not effective parameters implementing those device laws. A card that accepts them has not thereby modeled breakdown, on-resistance or gate charge; inspect the effective channel/charge parameters and verify the corresponding observable.

## BJT

1. Jointly constrain forward transport, current gain versus collector current, output effect, saturation and leakage under their own conditions.
2. Treat `fT`, capacitance and storage/switching time as different observables. `fT` alone cannot identify stored charge or reverse recovery.
3. Add breakdown, temperature or self-heating only from source-supported relations; absolute maximum voltage is not a breakdown model parameter.
4. Validate active-region and saturation behavior under finite loads, then add frequency or charge checks only when those behaviors are claimed.

## Diode, Zener and TVS

1. Use one compatible forward/reverse I-V relation for the published current-voltage anchors. A Zener/TVS breakdown voltage and surge clamp voltage must be simultaneously consistent when both are claimed.
2. Represent depletion/diffusion charge over its documented bias and frequency range. A capacitance endpoint does not establish reverse recovery.
3. Add recovery, pulse energy, thermal impedance, avalanche or survival behavior only from corresponding waveform/energy evidence and conditions.
4. Validate the material DC anchors, isolated capacitance/charge behavior, and a representative recovery or pulse case only when implemented.

## Polarity-aware fixtures and model interfaces

- **Bias direction follows carrier polarity.** NPN/N-channel and PNP/P-channel devices need different emitter/source returns, collector/drain load returns and input common mode. An NPN-oriented fixture applied to a PNP device can produce a finite but saturated operating point that hides the defect. Derive the fixture from the declared polarity and confirm the active region from the sign and magnitude of VCE/VDS; for a PNP differential pair the input common mode must sit near the positive rail so the collectors remain reverse-biased.
- **Body-diode direction is part of the port contract.** For an N-channel MOSFET the body diode conducts source-to-drain; for a P-channel device it conducts drain-to-source. Verify forward conduction with a current-limited fixture. A reverse test that reaches breakdown is not a body-diode check.
- **Primitive card versus subcircuit.** Keep model-card instances (Q/M) and subcircuit instances (X) distinct, and verify declared pin order empirically before attributing a mismatch to parameters. A wrong prefix or pin order is an interface defect, not an electrical result.
- **Extra high-current card parameters.** Before accepting an extracted card that uses quasi-saturation or other vendor high-current keywords, confirm the target engine implements them and run a saturated-switch transient in addition to an active-region DC point. Hard-saturation nonconvergence is a documented interface/model limitation; do not hide it behind global tolerances. A supported simplification must retain the claimed active-region behavior and state the lost saturation detail.
- **Sense the declared branch.** For parallel devices, bridge outputs and body-diode tests, place the current sensor in the branch that carries the load current. A magnetizing-current measurement in a parallel inductor is not the load current and can make a valid model look inactive.

For every class, retain source statistic, temperature, bias, fixture, curve-digitization uncertainty, extrapolation policy and parameter coupling. If evidence cannot identify a material mechanism, record the missing observable and use impact; a lower-order model is acceptable only within the user's scope. Otherwise the requested model remains incomplete, rather than guessing internal physics or silently narrowing the contract.

For reverse breakdown/clamp scope, derive VBR at its test current and VC at surge current from the same stated reverse I-V law. An unchecked linear series-resistance estimate may disagree with the primitive breakdown law. Check both source-conditioned anchors; a static endpoint does not establish pulse energy or survival.
