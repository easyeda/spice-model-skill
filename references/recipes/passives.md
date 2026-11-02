# Passive, magnetic, and resonant component synthesis

A passive part is not automatically an ideal element. Build the lowest-order model that preserves every source-supported behavior material to the intended circuit, frequency, bias, temperature, power, waveform and lifetime range. If the datasheet supports only nominal value and tolerance, an ideal element or a parameterized corner model may be the highest defensible fidelity. Do not invent ESR, ESL, coupling, core loss, thermal mass, aging, noise or nonlinear coefficients from package appearance or a related part.

## Common evidence and architecture decisions

Fix the exact manufacturer part number, construction or dielectric/core family, case/package, terminal arrangement and rated operating envelope. Separate initial tolerance, production limit, temperature coefficient, voltage/current bias, frequency dependence, aging and absolute or surge ratings. They are different effects and must not be collapsed into one nominal value.

Select model order from the observables needed by the circuit:

- A nominal low-frequency use may need only one ideal primitive plus a tolerance parameter.
- A finite-band impedance use needs a source-backed RLC or passive rational/lumped network across the declared band.
- Bias-, temperature-, power-, or history-dependent use needs an explicit constitutive or state relation supported by corresponding curves or coefficients.
- A pulse, energy, lifetime, destruction or safety rating does not define a waveform or failure model. Add those behaviors only with sufficient dynamic and thermal evidence.

Preserve passivity unless the physical part includes an active or externally powered mechanism. A fitted impedance network must not create energy, negative loss or unstable poles within its declared domain. State interpolation, extrapolation and endpoint behavior for every fitted table or curve.

## Resistors, shunts, and networks

Start with nominal resistance and tolerance at the stated reference temperature. Add TCR from its documented law and range; add power coefficient or self-heating only when dissipation dependence and thermal resistance or transient thermal data are available. Voltage coefficient, excess noise, current noise, pulse overload and long-term drift are separate claims.

Use series inductance and parallel capacitance only when impedance/frequency or construction data identifies them. A single measured frequency point cannot identify both parasitics uniquely. For precision shunts and resistor networks, preserve Kelvin terminals, shared substrate temperature and ratio tracking when those are material and sourced.

## Capacitors and supercapacitors

Separate nominal capacitance/tolerance from DC-bias, AC-amplitude, frequency, temperature and aging dependence. For a linear band-limited model, derive ESR, ESL and capacitance from impedance magnitude/phase, dissipation factor, Q, self-resonant frequency and the exact test conditions. A dissipation factor at one frequency identifies a local loss relation, not a universal broadband ESR.

Use charge-form behavior when capacitance depends materially on voltage: construct `q(v)` so `dq/dv` matches the sourced differential capacitance, remains finite over the declared domain and conserves terminal charge. Do not stack an external nonlinear charge block on top of a primitive capacitance that already represents the same charge. Add leakage, dielectric absorption, slow relaxation or supercapacitor diffusion ladders only when time-domain or multi-frequency evidence identifies them.

Rated voltage and stored-energy calculations constrain scope but do not establish breakdown, lifetime or failure behavior. Electrolytic polarity and reverse-voltage limitations must be explicit.

## Inductors, chokes, and ferrites

Separate small-signal inductance, DCR, Q/core loss, current-bias dependence, saturation, impedance versus frequency and self-resonance. A nominal inductance plus saturation-current rating does not identify the complete `L(I)` curve. Use a linear R-L-C model for the band it supports; use a source-fitted passive network for broadband impedance; introduce nonlinear flux only when bias or B-H evidence is sufficient.

Core loss depends on frequency, flux swing, waveform and temperature. Do not turn one Q or loss point into a universal resistor. Ferrite-bead impedance commonly contains both resistive loss and reactive behavior; fit the complex impedance or an equivalent network rather than treating the magnitude curve as a pure resistance.

## Transformers and coupled magnetics

Preserve winding polarity, turns ratio, winding resistances, magnetizing inductance, leakage inductance, coupling and interwinding/self capacitance when the source and use make them material. Do not assume `K=1`. Open-circuit and short-circuit impedance, insertion loss or equivalent-circuit data can constrain different branches; keep their test conditions distinct.

Add saturation, hysteresis, remanence or frequency-dependent core loss only when the datasheet/core data and geometry identify the required relation. A core material curve alone may be insufficient for a finished transformer without turns, core dimensions, gap and winding data. Declare the remaining construction inputs instead of guessing them.

## Thermistors, PTCs, varistors, and sensor-like passives

For NTC/PTC parts, implement the published resistance-temperature table or stated equation over its range. A beta value is interval-specific; do not extrapolate it as an exact global law. Add self-heating and response time only with dissipation factor, thermal resistance/capacitance or transient curves and an explicit ambient/fixture.

For MOVs and other varistors, build one compatible I-V relation from leakage, reference and clamp anchors under their stated pulse conditions. Surge-current and energy ratings are not normal constitutive points and do not establish repetitive life or failure. For LDRs, RTDs, strain gauges and similar passive sensors, preserve excitation, loading, temperature and hysteresis conditions; introduce cross-sensitivity only from evidence.

## Crystals and resonators

Use a Butterworth-Van Dyke or another documented equivalent network only when series/parallel resonance, motional parameters, shunt capacitance, Q, load capacitance or equivalent data can constrain it. Keep frequency tolerance, temperature curve, aging and drive-level dependence separate. A resonator model does not by itself prove oscillator startup, loop gain, drive limit or phase noise in a surrounding circuit.

## Minimum validation by claimed behavior

- Nominal/tolerance claim: direct value or bounded parameter check at the documented reference condition.
- Frequency or resonance claim: complex impedance/admittance, phase or resonance metrics at enough independent points to distinguish the chosen network order; fitting points alone do not prove extrapolation.
- Bias/current/temperature claim: independent source-conditioned points or bounds spanning the declared dependence and any material knee.
- Nonlinear charge, flux or thermal-state claim: endpoint plus derivative/integral or transient-energy checks that match the constitutive law.
- Coupled magnetic or multi-terminal network: polarity/ratio and at least one interaction case that exercises coupling, leakage or shared thermal behavior.

Retain the exact fixture definition used by the datasheet where practical. Fixture parasitics, de-embedding, measurement frequency and signal amplitude can dominate passive-component data; disclose them rather than fitting them silently into the device.

Use the shared [charge/flux](../mechanisms/charge.md), [noise](../mechanisms/noise.md) and [temperature/electrothermal](../mechanisms/temperature.md) recipes for these mechanisms and implicit native behavior. Do not duplicate their constitutive rules in a family-specific patch.
