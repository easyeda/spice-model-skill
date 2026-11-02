# Noise mechanisms

## Scope and evidence

Apply when noise is material, and audit implicit native noise whenever a macro-model contains noisy primitives. Record input/output reference, voltage/current ASD (V/sqrt(Hz), A/sqrt(Hz)), PSD (squared units/Hz), frequency, bias, temperature, source impedance and bandwidth. RMS, peak-to-peak, spot ASD and integrated noise are not interchangeable. A peak-to-peak/RMS ratio needs a bandwidth, duration and statistical assumption.

For uncorrelated sources, output PSD is the sum of |H_i(f)|^2 S_i(f). Correlated sources require cross-spectral terms; do not invent correlation from two marginal curves. Integrate **PSD**, then take the square root for RMS. A log-frequency plot does not change integration from df to d(log f).

## Audit implicit native noise

Ordinary ngspice resistors produce thermal noise by default: open-circuit voltage PSD 4 k T R and short-circuit current PSD 4 k T/R (one-sided conventions). T is kelvin. Native semiconductor models can contribute shot, thermal and flicker noise using model-specific defaults/parameters. Deterministic behavioral sources do not acquire physical noise merely because their DC/AC transfer is realistic.

Mathematical state resistors, internal conductances and numerical bleeders are not automatically physical noise sources. Explicitly use `noisy=0` for a resistor representing a deliberately noiseless mathematical mechanism. Preserve noise for physical resistors, or replace it with a documented equivalent without double counting. ngspice behavioral resistors have a different default: noise is disabled unless `noisy=1`; verify the selected element form.

**Discriminating check:** rescale mathematical state capacitance, conductance and drive together while preserving deterministic transfer. User-visible noise should remain invariant if physical noise parameters did not change. Multiplying C, G and gm by 100 leaves gm/(G+sC) unchanged, but an unreviewed ordinary state resistor changes its output thermal ASD by a factor of 10. This is a modeling defect, not physical noise evidence.

## Construct a source-supported model

1. Retain a suitable manufacturer/native noise model after checking bias dependence and analysis support. Avoid adding a second source for noise already represented by the core.
2. For behavioral op-amps, distinguish input voltage noise, each input's current noise and source-impedance transfer. A voltage-noise-only model cannot reproduce current-noise growth with source impedance. Add output-stage noise only when evidence identifies an additional contribution.
3. A noiseless controlled source can transfer noise from an isolated resistor. At reference temperature T0, Rn = en0^2/(4 k T0) gives an equivalent voltage source with appropriate gain/injection. Provide a valid reference and avoid altering signal loading. This inherently scales with sqrt(T) unless a separately sourced temperature law compensates it. It is a DERIVED equivalent, not an identified internal resistor.
4. For colored noise, use a suitable native mechanism, supported OSDI noise source, or finite-band causal filter driven by independent white sources. Identify coefficients against a PSD curve and state approximation error/band. A `hertz`-dependent deterministic B source changes transfer; it does not generate random noise. One corner frequency does not identify an arbitrary colored spectrum.
5. Use a separate stochastic realization for transient noise. `TRNOISE` amplitude and sampling interval are not an ASD specification. Account for sample/hold spectrum, filtering, bandwidth and seed/ensemble. Changing timestep or noise sampling interval can change realized noise. One seed or short trace cannot establish a statistical bound.

When bias-dependent PSD is implemented through amplitude weights, audit endpoint derivatives as well as PSD sums; a zero-valued noise signal can still leave an invalid Newton derivative. The endpoint construction and discriminating quiet-transient check are owned by [numerical diagnosis](../verification/numerical.md#endpoint-derivatives-and-state-initialization).

## Validate the selected analysis

Use native `.noise V(out[,ref]) input_source dec|oct|lin ...` for stationary small-signal noise about the solved operating point. The input source must describe the signal gain used for input referral. Export output/input spectra from the noise plot, verify actual frequency coverage, and check spot points and integrated RMS over the declared band. ngspice normally reports spectral densities as ASD unless `sqrnoise` changes the convention; explicitly record that choice before integrating exports. Inspect contributor summaries when unwanted internal noise is suspected.

Repeat only relevant biases, source impedances and temperatures. Use state-rescaling and noise-off controls where they discriminate double counting. Ordinary `.noise` does not establish oscillator phase noise, switched-circuit cyclostationary noise or sampling alias behavior. A transient statistical study needs an appropriate stationary window, estimator normalization, bandwidth and sufficient independent data.

Source: ngspice 47 User's Manual sections 3.3.1/3.3.4 (resistor noise), 4.1.7 (transient noise), and NOISE in chapters 11/13. See the [official manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf); qualify semantics against the actual runtime.
