# ngspice Native Expression and Model-Card Contract

Read this contract before writing or translating any B source, expression-controlled element, `.param`, `TABLE`/PWL relation, nonlinear measurement, or primitive `.MODEL` card. It prevents parser-compatible text from silently implementing the wrong equation or omitting a claimed primitive behavior. These rules use ngspice native semantics; a PSpice, LTspice, or vendor-library spelling is not native merely because a compatibility mode accepts it.

## Parser and source rules

- Netlist directives and `.control` commands are different contexts: for example `.tran` in a deck becomes `tran` inside `.control`. Do not copy the leading dot between them; check parameter visibility and command order in the actual receiving context.
- A B source has explicit positive and negative terminals and exactly one of `V=expression` or `I=expression`. The positive-to-negative orientation defines the voltage; positive current enters the positive terminal. Do not infer a branch-current sign from a node name.
- Use `V(node)` or `V(node_plus,node_minus)` for voltage. For a portable measured current, place a named 0 V sense source in the intended branch and use `I(Vsense)`. Do not assume resistor, B-source, or hierarchical-instance current names are portable across cards or compatibility modes.
- Inside a subcircuit behavioral expression, reference an external node's voltage explicitly, such as `V(VCC)` or `V(VCC,VSS)`. A bare token such as `VCC` is interpreted as a parameter name in an expression and can fail with an undefined-parameter diagnostic; it does not mean the voltage at that node.
- Use a B-source (`Bname n+ n- V=expression`) for a voltage computed from an expression. Do not replace a voltage-source value with `Vname n+ n- value={expression}` and assume equivalent behavioral evaluation; validate the exact card type and syntax on the target engine.
- Preserve primitive element token order exactly. A voltage-controlled switch is `Sname N+ N- NC+ NC- model`; an extra or missing token changes how nodes and the model name are parsed. For nested ternaries, inspect balanced parentheses and the fully expanded final expression.
- Do **not** write `if(condition, true_value, false_value)` in a B-source or parameter expression. The native conditional expression is `condition ? true_value : false_value`. Put whitespace before `?`, parenthesize nested conditionals, and keep this grammar separate from the `.control` language, whose `if` command has different syntax.
- Do **not** assume `LIMIT(x, low, high)` or `limit(x, low, high)` is a native B-source clamp. It is not in the native B-source function set. A vendor file may define a separate `.func LIMIT`; if so, preserve and audit that definition rather than treating its name as a built-in. Use an explicit ternary clamp, a documented PWL relation, or a smooth limiter.

```spice
* Exact hard clamp: discontinuous derivative at both rails.
Bclip out 0 V = V(x) < {VLO} ? {VLO} : V(x) > {VHI} ? {VHI} : V(x)
```

- Parameters are expanded during circuit setup; node voltages and source currents are evaluated during simulation. Define each `.param` before use, quote or brace it only where the receiving card requires front-end expansion, and avoid names that collide with nodes, elements, or analysis variables.
- Do not assume a mathematical constant is available in every expression context. In a target-engine probe, `pi` evaluated as expected inside a B-source expression, but `.param TEST={2*pi}` failed with `Undefined parameter [pi]`. When a `.param` expression needs π, define it explicitly first (for example `.param PI=3.141592653589793`) and verify the final library with the target engine; confirm constants separately in other expression contexts.
- When a primitive capacitor value comes from a subcircuit parameter, use a brace-delimited expression, for example `C_COMP COMP AGND {CCOMP} IC=0`. A bare identifier in the value position may be read as a capacitor model name; ngspice can report `can't find model 'ccomp'` while still returning process exit code 0 and producing operating-point data. Treat any such model-resolution warning as a load failure, inspect the complete target log, and verify the corrected final library unchanged.
- In a B source, `time` is zero in AC analysis and `hertz` is zero in transient analysis. Do not use either one to imply an AC or transient behavior that the expression cannot have in that analysis.

## Behavioral capacitors and terminal charge

- `Q=expression` is a behavioral **capacitor** form: write it on a `C` element with two explicit terminals, for example `Cq p n Q={q(V(p,n))}`. It is not a B-source parameter; `Bq p n Q=...` is invalid ngspice syntax. `C=expression` and `Q=expression` are alternative capacitor constitutive forms, not two properties to stack on one element.
- For `Cq p n Q={q(V(p,n))}`, the branch charge is `q(V(p,n))` and the capacitor current is `dq/dt` in the named element direction. The two terminals receive equal and opposite charge. Preserve this orientation when composing G-S, G-D, D-S, or other pairwise terminal-charge elements.
- Use the [charge mechanism](../mechanisms/charge.md) for source-anchor, derivative, multi-terminal conservation and fixture rules.
- For a native CLI target, run the [native charge smoke deck](../execution/probes/native-charge-smoke.cir) once before accepting a new behavioral-capacitor syntax family. Then load the unchanged final library and run only the source-conditioned analyses that exercise the claimed charge relation.

## Native `.MODEL` card requirements

- A datasheet label is not automatically a keyword for an ngspice primitive card. Before using a primitive `.MODEL` parameter to support a declared material behavior, verify that the selected native ngspice build recognizes that exact keyword for that exact primitive type. Do not transfer a parameter name between diode, BJT, MOS, or vendor-model dialects by resemblance.
- Load the final, verbatim delivery library through the target interface. A source-conditioned run with explicit load-diagnostic checks can establish this; use a separate minimal fixture when isolation is needed. Treat an `unrecognized`, `ignored`, malformed-continuation, or other parser diagnostic associated with the final library as unresolved: ngspice recovery does not implement the intended parameter or make the library delivery-ready.
- A final library must load without parser warnings. Write continuation and closing syntax that the target interface accepts verbatim; never rely on automatic replacement, commenting, or recovery of a line in a `.MODEL` statement.
- If an unsupported primitive keyword was intended to implement a declared behavior, compare relevant supported representations before narrowing scope. Use a supported subcircuit mechanism when it can retain the source-backed equation and coupling; otherwise record the reviewed sources, lost observable and circuit impact. Only a user-explicit narrow contract may omit a material requested behavior. Do not retain the behavior claim merely because the rest of the card loads.
- When the parameter supports a material claim such as reverse breakdown, run one source-conditioned endpoint after the clean load check. The endpoint confirms behavior, while the load check confirms that the target interface retained the intended parameter. Keep both checks limited to the affected claim.

## Native functions and limiting laws

These functions are mathematical operators, not proof of a physical clamp, current limit, or state machine. Choose a form whose derivative and out-of-range behavior match the declared model scope.

| Form | Native behavior | Modeling rule |
|---|---|---|
| `u(x)` | Unit step: 0 for `x < 0`, 0.5 at zero, 1 for `x > 0` | A discontinuity. Use only for an intentional topology/state boundary with DC paths on both sides. |
| `u2(x)` | 0 below 0, `x` from 0 to 1, 1 above 1 | A bounded ramp with corners at 0 and 1. It is not a smooth saturation. |
| `uramp(x)` | 0 below 0 and `x` at or above 0 | `max(x, 0)` with a derivative kink at zero. It does not cap the upper value. |
| `tanh(x)` | Smooth odd compression when supported by the selected engine | Use a dimensionless argument, for example `Vmid + Vspan*tanh((x-Vmid)/Vwidth)`. This changes small-signal gain and never reaches an exact rail; verify the target interface and resulting slope. |
| `abs`, `min`, `max`, ternary | Exact but kinked or discontinuous selection | Use only when the non-smooth boundary is part of the intended equation. Do not add them casually to suppress convergence symptoms. |
| `exp(x)` | ngspice limits the argument for convergence | This internal safeguard is not a physical output clamp. State any intended range and protect the model from unintended large arguments. |

Names that resemble standard mathematical functions are not necessarily available in ngspice expressions. Check the selected engine's native function list and compile a small probe for every unfamiliar function or operator before using it in a device model. A tested ngspice expression evaluator rejected `MOD()` and `IDT()` as unknown functions. For bounded integer modulo, derive the remainder from the quotient and `floor` only after checking endpoint and domain behavior. For an integral state such as phase, write an explicit state equation with a capacitor and behavioral current source; derive the branch-current sign and units from `i=C·dv/dt`, set a defined initial state, and verify a constant-rate probe against `Δstate=rate·Δt` before embedding it in a larger model.

XSPICE bridge model-card parameters are static; see [state/interface recipes](../recipes/state-interfaces.md) for supply normalization and analog boundary design.

For a smooth limiter, select a width from a physical transition, measurement resolution, or explicitly declared numerical representation. Do not select it solely because one testbench converges. If a hard rail is required by the public contract, use the ternary or PWL form and then check DC, traversal through both knees, and the affected transient behavior.

## Domains, powers, units, and tables

- Guard every divisor, `ln`, `log`, `sqrt`, and fractional power over startup, power-off, reverse-bias, and all declared parameter corners. A finite nominal operating point does not prove the expression is defined.
- `pow`, `**`, and `^` use absolute-value behavior for a negative base in native B-source semantics; `pwr` preserves the sign differently. Never substitute one for another without checking the equation over negative and fractional inputs.
- Audit each translated literal. In ngspice, `m` and `M` mean milli; use `MEG` for mega. Record written literal, intended SI value, and the resulting model quantity for every translated resistance, capacitance, current, gain, and frequency.
- A PWL relation needs finite, strictly increasing abscissas, units, a source curve, and an explicit endpoint policy. Native PWL continues linearly outside its knots unless the relation itself supplies endpoint plateaus or an explicit conditional clamp.
- Do not infer that `TABLE` syntax denotes a callable B-source function. In a tested native ngspice target, `pwl(x, x0, y0, ...)` was accepted as a B-source expression while `table(x, ...)` was rejected as an unknown function. Probe the exact expression form on the selected target; use PWL only with explicit ordered knots, units, source conditions, interpolation and endpoint behavior.
- Translate one semantic feature at a time. A vendor expression that parses in a compatibility mode must still be checked for sign, units, operating-point derivative, and out-of-range behavior through the selected native ngspice build.

## Minimum native check

Before accepting a new expression family on a native CLI target, run the tiny [native expression smoke deck](../execution/probes/native-expression-smoke.cir). These checks cover native ternary syntax, `u`, `u2`, `uramp`, `tanh`, and an explicit hard clamp. Then run only the model analyses affected by that expression: DC for domains and signs; AC when its derivative affects small-signal behavior; transient only when the expression governs a state transition or timing claim.

Run a generic smoke only when a new or changed expression family, translator or target interface makes its semantics uncertain. Reuse applicable evidence for unchanged syntax/runtime instead of repeating that probe per device. Inspect and load each actual generated library: a generic smoke with unrelated expressions cannot certify the final text. Native expressions must not emit control-language constructs such as `if(condition, a, b)`. If a probe fails, correct the syntax/translation cause before changing device parameters. The affected regression set contains only users of that changed syntax/runtime and its discriminating probe.

For `Q=` behavior, perform the source-anchor/derivative audit before the device bench; run the generic native charge smoke only when the card syntax or target support is unresolved. That smoke's forced-voltage operating point checks parsing only. It does not measure `dq/dv`, dynamic current, charge magnitude, terminal-charge conservation, Miller behavior or switching accuracy; those require the actual implemented relation and a discriminating source-conditioned check.

Before accepting a new or translated primitive-card syntax on a native CLI target, run the tiny [native model-card smoke deck](../execution/probes/native-model-card-smoke.cir). It only establishes the reference continuation form. The real check must include the complete final delivery library, unchanged, and must reject every library-associated parser warning before a material claim is accepted.

These smoke decks are parser and elementary-semantics checks. They do not qualify a device model, replace a physical load, or prove convergence for a larger nonlinear network. Store the target runtime identity and the finite requested vectors; reject a success exit with missing values or error-bearing logs.

## Analysis execution and measurements

- Start each deck with a title/comment line. Classic SPICE syntax treats the first line as the title; a directive placed there is not executed.
- In batch mode, an analysis may be skipped when no output directive selects its vectors. Add `.print`/`.plot`, use a `.control` block, or verify that the requested analysis actually produced data. Do not treat a missing table as a pass.
- Combining several analyses in one deck is target-build dependent. In particular, `.op` followed by `.ac` and `.dc` followed by `.ac` have been observed to run only part of the requested set on some builds. Use one analysis per deck or a verified `.control` sequence when each result is required.
- `.meas` accepts a narrower expression grammar than `.control`. For AC magnitude use a supported magnitude vector such as `vm(out)` and convert to dB in the evaluator; a `db(v(out))`/`vdb(out)` argument may be rejected as an unknown vector. Confirm that every requested measurement name appears exactly once in the intended analysis.
- A temperature sweep may not support `.meas dc` at all (`no such vector as ... v-sweep`). Either parse the printed sweep table or run separate operating points at each temperature; do not report the measurement as a model failure.
- Operating-point and DC tables are parsed by row name (`out 1.23e+00`), not by the `v(out) = ...` form used by `.meas`. Use a named 0 V sense source for a portable branch current.
- Avoid ambiguous or tool-reserved node names in `.print`/`.meas` directives; use explicit names and verify the parser's response.
- A model parameter dump can contain `-nan(ind)` for unused internal parameters or at an analysis corner while the solved vectors are finite. Use the analysis vectors and requested measurements as the result oracle; scanning the whole log for the substring `nan` produces false failures.

## Review checklist

Before loading, match every `.SUBCKT` with its `.ENDS` (including names when supplied), check the exact declared pin count and order at each instance, resolve referenced definitions/dependencies, and verify that default parameter values and derived expressions are finite in their required domains. Check the final expanded text rather than a template with missing values. These preflight checks do not replace the actual final-library load.

Before accepting an expression or primitive card, inspect the actual expanded text, B-source orientation, current-sense direction, conditional grammar, limits outside the nominal range, parameter units, domain guards, derivative continuity, table endpoints, final `.MODEL` card keywords and continuations, and target-build log. Verify the complete final `.SUBCKT` entry using its declared external pin order and instantiate that top-level subcircuit in the final load/behavior check; a helper subcircuit or isolated expression probe cannot establish that the delivered interface works. Keep the smallest reproducer only when a syntax or semantic risk has been found.

## Primary reference

This contract follows the official ngspice User's Manual sections for B-source syntax, native functions, ternary conditional grammar, `u`/`u2`/`uramp`, powers, PWL, and parameter evaluation. Use the manual that matches the available ngspice engine when practical. The executed target interface remains authoritative for model-card keywords, syntax not covered by the consulted manual, and compatibility-mode behavior; no particular ngspice release is required.
