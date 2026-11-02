# Op-amp construction recipe

These are DERIVED behavioral design equations, not a universal silicon schematic or a qualified library core. Use parameters only at their documented conditions and retain explicit applicability limits.

## 1. Error, input loading and supply reference

Define all signal voltages relative to the physical negative rail or another explicit local reference. Preserve input bias current signs and return them to a real supply path. Model common-mode and differential input impedance separately when supported.

One usable error equation is e = vplus − vminus + Vos + kcm·(Vcm − Vcm0) + kps·(Vs − Vs0).
Vos and coefficients need provenance and conditions. A CMRR/PSRR magnitude supplies a bound, not the sign or a full frequency response. For CMRR specified in dB, |kcm| = 10^(−CMRR/20) only for the corresponding input-referred ratio; check the vendor definition of PSRR before converting it. If only a magnitude is given, retain a signed parameter or bounded uncertainty rather than inventing a typical sign, distribution, or correlation. Do not implement common-mode range as an invented phase-reversal or protection threshold.

For average bias IB and signed difference ΔIB, Iplus = IB + ΔIB/2 and Iminus = IB − ΔIB/2. A published IOS = |ΔIB| does not fix its sign or prescribe a typical mismatch. Preserve any vendor input convention rather than replacing it with that formula blindly.

Account for input-network cross-contributions. Two identical input-to-reference legs Rleg, Cleg present Rleg/2 and 2·Cleg for common-mode excitation, but contribute 2·Rleg and Cleg/2 between the inputs in differential mode (with the defined reference held). Adding the full published differential branch on top may double-count its capacitance/conductance. Solve both equivalents under the manufacturer's measurement definition. If that requires a negative residual passive element, the assumed topology/definition is inconsistent: use an explicit modal admittance formulation or a source-supported topology instead of a negative “parasitic.”

## 2. Couple gain, pole, bandwidth and slew in one state

For a dominant internal voltage x with capacitance Cc and loss conductance Gc:

    Cc·dx/dt = limit(gm·e, −Ineg, Ipos) − Gc·x
    A(s) = K·gm / (Gc + s·Cc)        (linear, unsaturated region)
    A0 = K·gm/Gc;  fp = Gc/(2πCc)

K is the small-signal gain of the downstream stage under the stated condition; include load attenuation. Only when this stage is effectively constant and the dominant pole approximation is valid:

    fu ≈ K·gm/(2πCc)
    SRout,+ ≈ K·Ipos/Cc;  |SRout,−| ≈ K·Ineg/Cc

Choose Cc as a numerical state scale, then derive gm, Gc and current bounds coherently. Cc is not an identified silicon capacitor unless supported by evidence. The leakage term, downstream poles and output current limit can reduce actual large-signal slew; do not claim I/C as an exact waveform prediction. Scale x and its current together if internal state amplitudes become extreme. Verify DC values and derivatives algebraically before running.

Treat open-loop gain, unity-gain bandwidth, dominant-pole placement, slew rate, compensation current, downstream gain and output loading as one coupled design problem. Changing gm, Gc, Cc, either compensation-current limit, downstream gain or output resistance requires rechecking the applicable DC bias, open-loop gain, crossover, phase, slew, settling and loaded swing. One published gain or bandwidth value does not uniquely identify the internal state. When the available evidence cannot independently identify the proposed parameters, use a simpler identifiable representation that preserves the identifiable external behavior; narrow scope only after the documented fallback decision and only for a user-explicit narrower contract.

An illustrative SPICE mapping of this equation is Cc from X to VEE, Rloss=1/Gc from X to VEE (with noisy=0 when it is a mathematical loss rather than a physical noise source), and a current source from VEE to X carrying limit(gm·e,−Ineg,Ipos). Do not also include −Gc·x inside that source. Alternatively include the full right-hand side in the current source and omit Rloss; review numerical conditioning explicitly. If adding a downstream RC pole, buffer the state or derive the full coupled nodal system; directly attaching an RC load invalidates the isolated one-state transfer above. Such a buffer is an internal behavioral representation, not the physical output stage.

If phase-margin/curve evidence needs a second pole, include it at architecture time. For an idealized two-pole loop at its *actual unity-loop-gain frequency* fc with fp1 ≪ fc and no significant zeros or load phase:

    PM ≈ 90° − atan(fc/fp2), so fp2 ≈ fc·tan(PM)

This is an initial derivation, not a general fit: solve magnitude and phase consistently, include feedback β and output loading, and do not use unloaded GBW as fc after adding the pole. A single GBW value cannot identify multiple poles, zeros or phase margin. Fit only identifiable features of published curves.

## 3. Make the output stage load-bearing

Define output drive as a causal admittance or state-mediated relation. Terminal current may depend on present terminal voltage and present or past internal drive, with explicit sign and return paths; it must not depend on a future output value or unconstrained ideal measurement current. When DC headroom, load swing, capacitive-load phase margin, or frequency-dependent output impedance are material together, derive one causal frequency-dependent output admittance and recheck those observables with slew and transient energy flow. Do not append an arbitrary series inductance, resistance, or clamp that duplicates the same output law.

Use a finite Thevenin/Norton drive with source and sink limits and local rails. In a simple resistive output stage j = (vdrive − vout)/Rout; available sourcing/sinking current limits j, not an ideal output voltage. Then Cload·dvout/dt + iload = j, so output loading, slew and swing interact without separate waveform patches.

Real Zout(f), rail headroom versus current, crossover and overload may need more structure. Do not interpret a 1 MHz output-impedance point as a constant resistor across DC and AC. Avoid counting the same output resistance twice in both a swing curve and a series resistor. Map positive and negative headroom curves using their own signed current axes; shared coefficients are unjustified unless the evidence supports symmetry.

Identify whether a published output-impedance curve is open-loop or closed-loop and establish its feedback factor, loading and bias. For a simple single-loop representation, Zclosed = Zopen/(1 + Aloop); this relation does not justify using a measured closed-loop value directly as an intrinsic output resistor, and multi-loop topologies need their own derivation. Fit output admittance and compensation together when capacitive-load evidence requires it. If endpoint load fits leave the dynamic architecture ambiguous, an unfitted intermediate load can discriminate it; this is a targeted check, not a universal sweep requirement.

For a Class-B stage, distinguish the compensation/drive state from actual terminal current. Cload·dvout/dt can reverse terminal current during a transition; using that sign to repeatedly disable the integrating state can create artificial self-reset. A finite drive dead zone with continued compensation-state motion is a possible representation, but width, asymmetry and timing need evidence or explicit assumptions. Do not inherit numerical dead-zone values from another device without evidence or an explicit assumption.

For a source or sink boundary specified by both current and rail headroom, derive a finite load line from the stated rail voltage, required current and allowed headroom. An ideal current source connected to an otherwise weakly constrained output node may select a fragile or physically meaningless operating point; it is not a substitute for proving load-bearing output behavior.

Document where each output/input current returns, plus quiescent supply current. External KCL is necessary but does not prove correct individual rail power or dissipation; controlled sources can create unphysical energy unless the power-port model is designed. Do not add output current to IQ twice.

## 4. Complete the rest of the declared scope before first run

Instantiate both channels and their independent state for a dual package. Share supplies and only source-supported shared behavior. Include the selected common-mode dependence, supply dependence, rail/current limits, dominant/extra states, loading, and evidenced startup/overload behavior in the initial candidate.

No fabricated UVLO, thermal shutdown, noise spectrum, temperature law or precise recovery time. List unavailable observables and their effect on intended use. Physical rail operation, zero supply and state equilibrium still require finite, defined equations; numerical definedness is not a claim of accurate power-off silicon behavior.

A compact model that covers these coupled behaviors can be more useful than a larger unidentifiable transistor reconstruction. This recipe supplies design relationships; acceptance still needs the selected independent evidence.

Apply the shared [noise recipe](../mechanisms/noise.md) to internal-state resistor noise, input voltage/current noise and integrated bandwidth. Apply [temperature](../mechanisms/temperature.md) to source-supported offset/bias/gain drift and any claimed self-heating; room-temperature fits do not identify those laws.

## 5. Large-signal usability invariants

Fitted gain, bandwidth and offset do not establish that an amplifier macromodel works in feedback. Verify these independent invariants before accepting a candidate:

- **Input polarity under feedback.** Increasing the non-inverting input with the inverting input held must move the output in the direction that closes a unity-feedback loop. Check open-loop polarity and a unity follower separately. A follower that settles at a rail, or a hysteretic comparator that never changes state, is a sign or topology defect even when a linear operating point looks plausible.
- **DC definition of every internal input node.** A chain of series sources and resistors terminated only by clamp diodes has no bias path. Every high-impedance internal node needs an explicit finite DC return; otherwise the solver can converge to a latched but meaningless solution.
- **Bounded internal state.** The dominant compensation state must have a finite, physically plausible excursion. If an ideal integrator can accumulate kilovolts during overdrive, recovery is set by the numerical state rather than the claimed slew or settling. Clamp or scale the state consistently with the output-stage limits, and verify a large-signal reversal.
- **Load-bearing output stage.** Represent source and sink current limits and rail-referenced clamps as finite load lines. An ideal voltage source behind a small series resistance can deliver arbitrary current into an exponential clamp; the clamp then fails to hold the node or forces vanishing timesteps. Use a causal current-limited output relation, or a documented linear clamp with stated slope and overlap, and verify short, overdrive and capacitive-load cases.
- **Feedback and large-signal regression.** Run every stability/bandwidth claim in the actual closed-loop topology and load. A unity follower step, a capacitive-load step and a hysteresis/comparator test are distinct large-signal checks, not substitutes for the AC gain point.
- **Numerical regularity of the declared ports.** Add only the input/output capacitance or conductance needed by the declared port behavior, and require the feedback/comparator fixtures to converge at a declared timestep. Do not use ideal hard branches for analog protection that the sources do not identify.

Record these as verified only for the conditions actually exercised. They are acceptance invariants, not parameters to fit.
