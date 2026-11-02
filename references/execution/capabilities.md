# Native mechanisms and analysis scope

Choose a representation for material source-supported observables, not to exercise the entire engine. Check an uncertain mechanism with the smallest discriminating circuit on the actual build; reuse evidence for unchanged semantics.

| Native route | Appropriate use and boundary |
|---|---|
| R/L/C, mutual inductance, transmission lines | Storage, loss, distributed propagation; preserve physical reference/energy and causal frequency dependence |
| Diode/BJT/JFET/MOS/VDMOS/compact models | Supported semiconductor laws; check exact parameters, native charge/noise/temp defaults and source applicability |
| E/F/G/H and B sources | Linear/nonlinear constitutive laws and explicit states; finite domains and valid derivatives matter |
| Hierarchy, parameter/functions, PWL/tables | Reusable architecture and source curves with defined interpolation/extrapolation |
| XSPICE A devices/bridges/custom code models | Events, transfer functions and mixed-signal behavior; required compiled modules and state/port semantics |
| Verilog-A through OSDI N devices | Custom compact/multiphysics laws; compiled ABI, supported language subset, solver/analysis and licensing requirements |
| Native digital co-simulation | Supported d_cosim/d_process routes when actual external logic semantics justify toolchain and lifecycle dependencies |
| OP/DC/AC/TRAN/NOISE | Independent operating-point, swept static, linear response, dynamic/state and stationary small-signal noise claims |
| TF/SENS/SP and other native analyses/control loops | Use full decks and corresponding result evaluators when the selected build supports the required semantics |

Reusable libraries normally contain definitions and dependencies, not commands that start analyses, select plots or quit the caller's session. Validation decks may use complete native `.control`, loops, `.lib`, `.options`, `.nodeset`, `.ic` and any supported element family. The helper's convenience API imposes no global device or analysis whitelist; full native decks remain available.

Important version-specific facts from the ngspice 47 manual:

- Native E-source LAPLACE syntax is not provided directly; relevant XSPICE s_xfer models implement causal transfer functions for AC/TRAN. The FREQ transfer path is AC-only and cannot establish time-domain behavior (sections 5.2.5-5.2.6).
- OSDI noise requires the supported solver path: the manual specifies Sparse 1.3 rather than KLU (section 9.2). Check actual solver selection, not only compilation flags.
- PSS is described as experimental with build-dependent availability; do not promise mature generic PSS/PAC/PNoise support. Ordinary AC/NOISE around DC does not represent periodically varying or autonomous-oscillator perturbations.
- Native d_cosim/d_process routes have external compiler/process and timing/state requirements (section 10.3); native-only does not mean toolchain-free.
- Model-card labels can be informational rather than effective equations (for example some VDMOS metadata). Exact supported parameter meaning matters more than parse success.

A missing module/build option is a configuration gap. An unsuccessful macro-model, timeout, or unsupported helper metric does not establish an ngspice ceiling. Compare relevant alternatives and state the specific lost observable/conditions before reporting a true limitation. A semantic probe proves its tested mechanism only.

Sources: [official manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf) and selected build documentation. The rules above were checked against release 47; later builds require checking changed behavior only.
