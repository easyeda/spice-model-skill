# Native runner and numeric evaluation

The executor accepts reviewed native ngspice decks without a device or directive whitelist. `.control`, `.lib` sections, `.options`, `.nodeset`, transmission lines, XSPICE and OSDI remain native engine features. A reusable model library normally contains definitions and dependencies, without analysis commands, `.control`, `quit` or a top-level `.end`; put those in the testbench. The executor does not enforce this design convention by parsing SPICE.

The modules have separate responsibilities:

- `native_runner.py` stages explicit inputs, initializes the selected engine, runs it and captures diagnostics.
- `analyses.py` optionally generates OP, DC, AC, TRAN or NOISE commands.
- `results.py` reads numeric exports, verifies their domains and computes metrics.
- `run_analysis.py` connects these parts through a JSON manifest and writes `result.json`.

These tools execute trusted, reviewed programs. A fresh working directory is not a security sandbox: native control commands can access files and invoke external programs. Relative paths organize inputs, not a device capability boundary.

## Invocation and minimal example

Use an available engine directly, or obtain one through the provisioning helper first. Python uses only its standard library.

```text
python scripts/run_analysis.py --manifest case.json --engine /path/to/ngspice --output /path/to/new-run
```

`case.json` and `divider.inc` are in the same directory. The latter contains `V1 in 0 2`, `R1 in out 1k`, and `R2 out 0 1k` on separate lines.

```json
{
  "schema_version": "ngspice-run/2",
  "entry": "divider.inc",
  "analysis": {"type": "op"},
  "vectors": [{"name": "out", "expression": "v(out)"}],
  "metrics": [{
    "id": "divider", "column": "out", "operation": "scalar",
    "expected": 1, "atol": 0.000001, "rtol": 0,
    "unit": "V", "source": "DERIVED: 2 V times 1 kohm / 2 kohm",
    "tolerance_basis": "Numerical allowance for the ideal divider equation"
  }]
}
```

The top-level optional fields are `test_id`, `inputs`, `temperature_degC`, `timeout_s` (default 60), `startup`, `environment`, `analysis`, `vectors`, `exports` and `metrics`. Unknown top-level fields, structured analysis/sweep/vector fields and duplicate JSON keys are errors; for example, `uci` is rejected rather than silently replacing `uic` with the default. JSON numbers must be finite; use numeric SI values for structured fields. `entry` and additional `inputs` are relative to the manifest directory. Declare dependency files, or directories to preserve an existing library hierarchy. Declared directories cannot contain links/junctions or contain the run output directory. Files are copied without rewriting their contents. Native include resolution still follows ngspice semantics; stage the hierarchy it expects, and explicitly declare nonstandard runtime assets.

The output directory must not exist. The runner creates `work`, `init/spinit`, `engine.log`, `ngspice.log` and `result.json`. An expected export already present in staged inputs is rejected before execution. Outputs are always read from this fresh run; no cache, old result JSON, caller-supplied `actual` or mandatory hash chain can substitute for numeric data. Preserve these working files when useful; long-term retention is optional.

## Structured analyses

| Type | Analysis fields | Meaning |
|---|---|---|
| `op` | `type` | One operating point; exported scale is explicit `index=0` |
| `dc` | `sweeps`: one or two objects, each with `source`, `start`, `stop`, `step` | Native voltage source, current source or `TEMP` sweep; first sweep varies fastest; positive and negative steps follow native order |
| `ac` | `spacing`, `points`, `start`, `stop` | `lin`: total points; `dec`/`oct`: points per decade/octave; positive frequencies |
| `tran` | `step`, `stop`; optional `start`, `max_step`, `ic`, `uic` | `start` defaults to zero; `max_step` defaults to `step`; `ic` maps node names to voltages, e.g. `{"out":1}`; `uic` is a boolean |
| `noise` | `output`, `source`, plus AC frequency fields | Example `output: "v(out)"`, `source: "V1"`; exports the spectral `noise1` plot |

`step` is the transient output/interpolation interval, not a promise of uniform internal timesteps. The runner checks the actual adaptive vector and maximum step. Native `tstart` suppresses earlier saved points; the first saved point may follow `start` by up to `max_step`. Sampling before that first point is rejected, not extrapolated. `.ic` with and without `UIC` has different native initialization semantics; choose from the circuit's physical initial state.

Each vector specifies a unique lowercase `name` and a native control-language `expression`. AC defaults to `complex: true`, generating `<name>_re` and `<name>_im`; other analyses default to a real column named `<name>`. Expressions are passed to ngspice; this is not an expression whitelist. NOISE commonly exports `onoise_spectrum` or `inoise_spectrum`. Output aliases must not collide with one another. Unsupported convenience forms, much larger grids, nested control loops and additional analyses use a full native deck instead of enlarging this adapter indefinitely.

## Native full decks and exports

Omit `analysis` and provide an explicit `exports` array. The `entry` deck runs unchanged, including its own `.control` block. Every required analysis needs a fresh numeric export and a domain contract; an undeclared analysis is not validated merely because another export passed.

```json
{
  "schema_version": "ngspice-run/2",
  "entry": "native.cir",
  "inputs": ["models"],
  "exports": [{
    "id": "spectrum", "path": "spectrum.tsv",
    "columns": ["frequency", "amplitude"],
    "domain": {"grid": [10, 100, 1000], "positive": true}
  }],
  "metrics": [{
    "id": "peak", "export": "spectrum", "column": "amplitude",
    "operation": "max", "minimum": 0.9, "maximum": 1.1,
    "unit": "V", "source": "DERIVED: declared sinusoidal stimulus and window",
    "tolerance_basis": "Declared spectral window and leakage budget"
  }]
}
```

The deck must generate that table, normally with `set numdgt=17`, `set wr_singlescale`, `set wr_vecnames`, `let amplitude = ...`, and `wrdata spectrum.tsv amplitude`. The table has one header and finite numeric rows of exactly the declared width. Export complex vectors as explicit real/imaginary columns to avoid ambiguous repeated scales. Full decks can export native FFT/spectral results or numeric event-derived observables. Arbitrary text logs and binary rawfiles are not accepted as these numeric tables.

A domain must declare an exact `grid`, an expected integer `count`, or `start` plus `stop` plus `monotonic` (`increasing`/`decreasing`). Add `positive` and `max_step` where relevant. A count alone validates length, not frequency/time coverage; use a grid or endpoints for those claims. Grid checks cap the internal rounding allowance `1e-14 + 1e-8 * abs(expected scale)` at one quarter of the nearest distinct requested scale spacing, so close points cannot be interchanged. This is not an electrical tolerance. Repeated grid values are allowed for declared nested sweep segments, with each row still checked against its requested position. Structured DC checks every inner-grid point and the outer-sweep repetition count. Metrics should also expose the outer sweep's physical effect; the repeated inner scale alone cannot establish its electrical correctness.

Structured sweep generation rejects intended distinct points that collapse at floating-point precision. For start/stop and max-step checks, the rounding allowance is additionally capped at 0.001 of the smaller positive declared span/max-step. A short interval or small timestep must not disappear inside a fixed absolute allowance or a large starting-coordinate relative allowance. Specialized evaluators must likewise keep coordinate uncertainty below the independent condition/event resolution; amplitude agreement cannot repair the wrong measurement condition.

## Metrics

Every metric requires `id`, `operation`, `unit`, `source`, `tolerance_basis`, and either independent `expected` with nonnegative `atol`/`rtol`, or numeric `minimum`/`maximum`. The expected values must come from source conditions or an independent derivation, never from the candidate's output. Optional `export` defaults to `analysis` for structured runs. Numerical comparison is `abs(actual-expected) <= atol + rtol*abs(expected)`.

| Operation | Actual value |
|---|---|
| `points` | Every row, or linearly interpolated samples selected by `at: [...]` |
| `scalar` | Exactly one row or one explicitly sampled point |
| `bounds` | All selected values tested against `minimum`/`maximum` |
| `min`, `max` | Extreme of selected values |
| `integral` | Trapezoidal integral on an increasing scale; inspect timestep/interpolation error for the physical claim |
| `crossing` | Linearly interpolated crossing of `level`; `direction` is `rising`, `falling` or `either`; `occurrence` defaults to 1 |

Select a normal column with `column`. For complex results, set `component` to `magnitude`, `phase_deg` or `phase_rad` and supply `real` and `imag` column names. `unwrap: true` unwraps phase before sampling. `at` must select at least one sample; empty metric selections are rejected. It performs interpolation without extrapolation; use a sufficiently resolved raw grid. `segment` selects a zero-based outer DC sweep segment for interpolation, timing or integration. Descending DC grids are accepted for point comparison; reverse/resample through an external evaluator for integration.

A crossing at the initial sample is not an observed transition. Plateaus are counted when the signal first reaches the threshold from the selected side. Specialized settling definitions, digital event protocols, multi-signal delays, cycle-aware energy, spectral window corrections, and other unsupported metrics require a separate deterministic evaluator reading the actual fresh exports. That evaluator must retain finite, domain, completion and independent-oracle checks; an adapter limitation is not an ngspice limitation. This helper does not infer units or certify the physical correctness of a chosen oracle.

## Initialization, modules and diagnostics

The runner invokes the selected executable with `-n -b -o <fresh engine.log>`. `-n` suppresses user `.spiceinit`; the process-local `SPICE_SCRIPTS` points to a generated `spinit` containing exactly the explicit `startup` command lines. Add required compatibility settings and `codemodel /absolute/path/analog.cm` or `osdi /absolute/path/model.osdi` there. `environment` contains explicit per-process environment overrides. Neither global user configuration nor the engine installation is edited, and OSDI is never globally unset. Module filenames, quoting and ABI must match the chosen build; retain actual load diagnostics. No implicit module inventory is treated as successful loading.

On timeout, Windows uses `taskkill /PID <launched PID> /T /F` with hidden windows; POSIX starts a separate session and kills its process group. The result records `timeout_cleanup`, including success or failure, and retains collected output. Only the PID owned by this invocation is targeted. The Windows shell-descendant path has a live regression; POSIX group cleanup requires runtime verification on a POSIX host. This is process cleanup, not containment of intentionally detached or daemonized descendants. Failed cleanup remains explicitly reported and must be resolved before assuming all work has stopped.

The log is captured through `-o` as well as stdout/stderr because some Windows builds leave the latter empty. Terminal analysis, parsing, load and failed-measurement errors prevent numerical PASS. Singular-matrix, gmin and source-stepping messages are retained as `solver_recovery_diagnostics`; they are attempts that may recover, not automatically terminal errors. The evaluator still requires complete finite outputs and valid grids. If metrics pass but any warning remains, status is `REVIEW_REQUIRED`, with metric results retained. Inspect whether recovery preserved the intended operating point, whether sensitivity needs a targeted check, or whether a parameter was ignored. The helper does not silently waive warnings or label a recovered numerical solution electrically qualified.

For Windows headless or batch calls, select the build's console executable when supplied (commonly `ngspice_con.exe`). A GUI-subsystem `ngspice.exe` can return without usable captured output under that invocation. Empty stdout/stderr alone is not failure when the fresh `-o` log and expected numeric exports are valid. If those artifacts are also absent or empty, the call provides no simulation evidence: retry the same relevant deck through the console executable with its matching startup/module configuration before diagnosing the model or asserting an engine limitation. The discriminating result is a fresh completed log and finite exports for that deck, not an executable name or exit code. Builds with a functioning console entry named `ngspice.exe` remain valid.

Statuses are `PASS`, `FAIL`, `EXECUTED` (complete declared exports, no electrical metrics), `REVIEW_REQUIRED`, `EXECUTION_FAILED`, `TIMEOUT`, `RESULT_ERROR`, or CLI `INPUT_ERROR`. CLI exit code is zero only for `PASS`/`EXECUTED`, one for completed non-pass reports, and two for invocation/input errors. These statuses are scoped to the declared test, not whole-device fidelity or application qualification.

## Migration and factual basis

`ngspice-run/2` replaces the archived `dc-test/1` and `ac-tran-test/1` helper APIs. Translate their circuit entries/dependencies, sweep specifications and independent metric expectations into this manifest; retained old schemas are not silently accepted. The old DC-bound parser, blanket singular-matrix failure checker and evidence-hash runner are removed from this candidate. Historical artifacts remain readable with their matching historical Skill version.

The native semantics follow the [ngspice manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf), release 47: analyses in chapter 11, control interpreter and `wrdata` (13.5.107), XSPICE chapter 8, and OSDI chapter 9. Release 47 was used for focused synthetic regression of these helpers; the tools do not impose that release on other supported builds. Passing synthetic resistor/RC/module cases does not qualify a real device or establish full engine capability coverage.
