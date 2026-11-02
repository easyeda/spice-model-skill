# Charge, flux and isolated port measurement

Apply to nonlinear capacitance, switching charge and magnetic storage. Distinguish differential capacitance from a charge/voltage ratio: q(v)=integral C(v) dv and i=dq/dt; generally q(v) is not C(v)*v. For nonlinear inductance use consistent flux linkage and differential inductance; do not combine arbitrary L(i) with an inconsistent energy claim.

Before simulation, evaluate charge at every source charge anchor and one-sided dq/dv at capacitance anchors and piecewise boundaries. Check signs, units, continuity and domains. Quantify smoothing effects on charge and derivatives. A parameter named Q_TARGET does not prove the assembled equation reaches it. Executable `C... Q=...` grammar belongs to [native syntax](../syntax/ngspice.md).

Charge and its relevant derivatives must remain finite at startup, reverse bias, power-off and throughout declared extrapolation. At an intentional derivative jump, record both one-sided derivatives and the source-supported reason; never hide a missing region with a discontinuous charge value or arbitrary added capacitance.

For multi-terminal devices, terminal charges sum to zero and the differential capacitance matrix follows the same charge functions and reference convention. A transistor capacitance matrix need not be symmetric; do not impose reciprocal-passive symmetry on active-device charge partition. Check derivative consistency of each charge function, common-mode invariance and declared bias range. Pairwise capacitors are a limited representation, not a universal multi-terminal surface.

For MOS curves at the same bias/definition, Cgd=Crss, Cgs=Ciss-Crss, Cds=Coss-Crss. Negative residuals require source/definition review, not invented negative parasitics. Check native charge before adding external capacitance/recovery. Body-diode I-V and depletion capacitance do not establish reverse recovery.

Start with the identifiable source-backed pairwise C/Q terms. Add residual multi-terminal charge only when independently identified and consistent with conservation and the measured trajectory. A fixed capacitor can be adequate locally and can produce an approximate Miller plateau; neither fact establishes full bias-dependent charge or switching accuracy. If the Qgd table, typical Miller width and integrated Crss disagree under their stated conditions, retain the source conflict instead of inventing compensating charge.

MOS Qg/Qgs/Qgd describe integrals along a documented multi-terminal trajectory, not independent capacitors. Before fitting, the channel law must produce the specified drain current at observed Miller Vgs/Vds. A valid constant gate-current fixture provides a realizable drain-current path and allows Vds to move. Forcing both drain current and prescribed Vds(t) does not reproduce that experiment. Retain simultaneous integral(ig dt), Vgs, Vds and Id through the Miller interval; compare with terminal-charge change. Do not infer a global q(Vgs) from one trajectory or invent residual charge to reconcile conflicting TYP curves and MIN/MAX tables.

For small-signal capacitance, define DC bias, one AC injection, current sign and every other port's AC return. Calculate Y=I/V and C=imag(Y)/(2*pi*f) only where that lumped interpretation is valid. An accidental ideal clamp can carry excitation current instead of the model. Current excitation alone does not establish a return. Compare extracted capacitance against the same charge derivative and a transient integral where switching is claimed.

## MOS capacitance fixtures

Use the source's stated bias, frequency and terminal definition. For the usual common-source, off-state capacitance definitions, hold S at a local AC reference, establish the required DC VDS/VGS, and apply the following separate small-signal fixtures:

| Observable | AC excitation and return | Measured current |
|---|---|---|
| Ciss = Cgs + Cgd | Excite G relative to S; D is AC-grounded while preserving DC VDS | Current entering G, divided by the applied VGS |
| Coss = Cds + Cgd | Excite D relative to S; G is AC-grounded at the specified DC VGS | Current entering D, divided by the applied VDS |
| Crss = Cgd | Excite D; hold G at AC ground through a current-sensing path, S at the local AC reference | Gate transfer current; with currents entering the device, Cgd = -imag(Ig/Vd)/(2*pi*f) |

A gate-excited equivalent transfer fixture may be used only after deriving its terminal relation. Source current orientation can reverse the reported sign: derive the sign from the actual sense-source terminals, never blindly use positive imag(Y) for Crss. Account for parallel feedback, controlled-source, supply and bias paths. Independent common-mode sources do not automatically isolate the desired charge branch. A finite DC bias with an unintended AC short at the excited port is an invalid measurement.

Sources: ngspice 47 manual sections 3.3.9/7.7; TI [SLUA618A, sections 2.3-2.7](https://www.ti.com/lit/ml/slua618a/slua618a.pdf). A mechanism probe does not qualify a device.
