# Delivery and temporary-file lifecycle

The default final directory contains all files needed to use the model and **one concise Markdown explanation**. Includes, lookup tables, required native modules/binary cores, licenses and necessary runtime dependencies are legitimate deliverables. There is no one-model-file quota. A shared/private engine installation normally lives outside the model directory.

Exclude benches, candidate revisions, raw/log files, fitting data, plots, validation JSON, hash manifests and evidence chains by default. A source PDF is not a runtime dependency: preserve user originals in place; copy source material only within the agreed delivery. The MD gives source document/revision/page references without archived extraction work.

## Lifecycle

1. Create a fresh task-owned scratch directory for extraction, construction notes, candidates, benches and outputs. [workspace.py](../../scripts/workspace.py) `create --parent DIR` returns its directory and ownership token. Keep shared engines and user originals outside.
2. During diagnosis retain the previous candidate, actual failures and correction hypothesis in this working area. Do not replace failures with a manufactured pass. Pending repair may retain the minimum recovery state while needed.
3. Prepare a dependency-closed final tree: resolve recursive `.include`/`.lib` references, model-specific tables/modules and licenses. Check native module/OSDI loading as well as text includes. Search for scratch paths; static inspection alone cannot prove runtime dependencies.
4. Copy selected files and the MD to the authorized destination. `workspace.py publish --workspace DIR --token TOKEN --destination NEW_DIR --file model.lib --file MODEL.md [--file ...]` preserves relative layout, creates missing authorized parent directories after validating selected files, and refuses existing destinations. If a necessary license also uses Markdown, identify the primary explanation with --description MODEL.md; dependency filenames are not restricted by extension. It checks ownership/file selection, not electrical validity or dependency closure. Authorized existing deliveries need staged replacement under the user's overwrite/version policy.
5. Run a relevant final-load/behavior check instantiating the **actual final bytes at final dependency paths**, from a working directory that cannot supply missing scratch dependencies. Use the same engine/configuration and inspect actual finite results. Check binary load/ABI where relevant. Keep this deck/results disposable. Resolve failures before declaring delivery complete.
6. After success, autonomously call `workspace.py cleanup --workspace DIR --token TOKEN`. It checks its generated root/marker, rejects links/junctions and removes only that root. It does not decide whether verification passed: inspect the real result first. Never clean user directories, old files, originals, shared engines or delivery trees. Do not use recursive wildcard cleanup.

For failure/interruption, state the unresolved issue and retain only active recovery state while needed. Remove disposable state on completion or when no longer needed; do not archive it indefinitely by default. Explicit audit-bundle requests can retain agreed files without changing the default.

## Concise MD

Use [the template](../../assets/model-description.md): identity, ordered pins/invocation, dependencies and actual engine/build, behavior/range, key source/derived/assumed choices, limitations and short factual verification summary. Material claims use behavior, conditions, error/bounds and evidence status, not a global maturity score.

Write the explanation in the user's language, remove template prompts, and omit irrelevant optional fields. Usually one to three sentences suffice for the verification summary; distinguish source comparisons from application checks actually performed. Without retained inputs/results, this declaration is not a replayable audit trail. Preserve original model comments and licensing notices.

Every MD produced with this skill must include the concise AI-generated model notice in the template, translated into the user's language while preserving both points: the model aims to reproduce source-supported device behavior as faithfully as possible, and complete reproduction of real electrical behavior is not guaranteed. Keep the notice separate from specific assumptions and verified coverage; it does not excuse omitted source-supported behavior, relax verification, or establish manufacturer endorsement. Check both points in the final MD. This rule does not require rewriting historical deliveries unless that work is requested.

## Model-file header notice

Every delivered model file (`.lib`, `.mod`, or equivalent entry model) must carry the same concise AI-generated notice as a `*` header comment at the top of the file, translated into the user's language while preserving both points above. Example header:

```
* =====================================================================
* AI-generated model notice
* This model was generated by AI from the cited datasheet and technical
* sources. It aims to reproduce the device behavior supported by those
* sources as faithfully as possible, but does not guarantee complete
* reproduction of the real device's electrical behavior.
* Verify against the manufacturer datasheet before use.
* =====================================================================
```

A delivered model file without this header is incomplete. The notice does not excuse omitted source-supported behavior, relax verification, or establish manufacturer endorsement. This rule does not require rewriting historical deliveries unless that work is requested.
