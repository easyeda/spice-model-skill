# Temperature and electrothermal mechanisms

## Static temperature and native defaults

Apply when temperature dependence is claimed or a primitive already has temperature-dependent laws. `TEMP` is operating temperature; `TNOM` is the reference temperature of model parameters. Device support varies: inspect the selected family. Where supported, instance TEMP overrides circuit temperature; otherwise DTEMP offsets it. Setting both does not add them: instance TEMP takes precedence.

Record source reference temperature, sweep interval and coefficient units. A coefficient in ppm/K is 1e-6/K; Celsius and kelvin differences are equal, but exponential and thermal-noise equations require absolute kelvin. Native semiconductor defaults can change behavior even without an explicit temperature fit. Label these laws as native-model assumptions pending source comparison; room-temperature calibration does not establish hot/cold behavior. Match TNOM to fitted parameter conditions.

For a sourced polynomial, R(T)=R(T0)[1+alpha(T-T0)+beta(T-T0)^2] over its documented interval. Preserve statistics and curvature; an unsigned drift bound is not a signed typical slope. A beta thermistor law R(T)=R(T0) exp[B(1/T-1/T0)] needs the applicable beta interval and kelvin. Prefer a source table or higher-order law if this approximation cannot meet curve uncertainty.

In B expressions, `temper` denotes circuit temperature in degrees C. Native instance-temperature parameters and a dynamically solved local thermal node are different mechanisms. Parameters expanded at setup are not automatically reevaluated continuously or after every interactive change: use the documented expression context and test an actual sweep. A global `.temp` does not create an electrothermal model.

**Check:** compare reference, hot and cold source anchors, including an interior point when curvature is claimed. Test TEMP/TNOM/DTEMP precedence on the actual primitive family. Recheck affected bias, gain, leakage, resistance, threshold, delay or noise. An imposed-temperature sweep does not establish self-heating.

## Dynamic self-heating

Require source-backed dissipation, thermal boundary conditions, Rtheta and relevant Ztheta(t) or time constants. For a single physical thermal state:

    Ctheta * d(DeltaT)/dt = Pdiss - DeltaT/Rtheta
    Tj = Tamb + DeltaT
    tau = Rtheta*Ctheta

Circuit analogy: voltage = kelvin temperature rise, current = watts, R = K/W, C = J/K. Feed Tj back into the temperature-dependent electrical laws; a thermal output without electrical feedback only reports temperature. For a supported five-terminal VDMOS electrothermal model, follow its temperature-node conventions rather than adding duplicate self-heating.

Pdiss is dissipated power, not blindly the product at an arbitrary signal port. Include relevant supply/return currents and separate delivered load power and stored electrical energy. Ideal behavioral sources can create/remove energy; a correct output waveform does not prove thermal power balance. Do not inject negative dissipation into a passive thermal network to hide a power-accounting error.

Use the supported boundary: junction-to-case with prescribed case temperature, or junction-to-ambient under a specified mounting/board condition. ThetaJA is not independent of cooling. A Foster fit reproduces thermal impedance under its fitted boundary; internal nodes are not physical layer temperatures and generally cannot form a physical material stack. Use a justified Cauer network or boundary transformation when composing thermal paths.

For multiple poles, fit Ztheta(t), preserving positive thermal R/C for a passive approximation, asymptotic Rtheta and measured time range. A steady Rtheta alone does not identify transient Ctheta. A shutdown threshold does not identify thermal mass or restart dynamics; source hysteresis/latency separately.

**Checks:** a constant-power step approaches DeltaT=P*Rtheta; a single pole reaches (1-exp(-1))*P*Rtheta at tau. Cooling returns to the ambient boundary. Check electrical feedback at two meaningful powers and resolving timesteps. Compare dissipated energy with thermal storage plus heat outflow. Distinguish electrical/thermal runaway from numerical failure. SOA and absolute maxima bound claims; they do not supply irreversible damage physics.

Sources: ngspice 47 manual sections 1.3, 5.1.1-5.1.2 and 7.7; device thermal characterization supplies parameters and mounting conditions. See [capabilities](../execution/capabilities.md).
