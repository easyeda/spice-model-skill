# Rule placement and promotion

Use this map during an authorized skill update. Learning a lesson does not authorize modifying the installed skill or another user's files. Keep detailed rules in one owner; other references link to it.

| Root cause / reusable knowledge | Authoritative home |
|---|---|
| Source authenticity, extraction, statistics, conditions, uncertainty | sources/evidence.md |
| Coupled equations, physical ports, states, identifiability, energy/cause structure | modeling/architecture.md |
| Native parser/card/expression semantics, static versus runtime evaluation | syntax/ngspice.md |
| Cross-family charge/noise/temperature or another reusable physical mechanism | mechanisms/<mechanism>.md |
| Family-specific topology and derivation | recipes/<family>.md |
| Engine provisioning/build/module support | execution/provisioning.md or capabilities.md |
| Runner construction/staging/output/metric contract | execution/runner.md and relevant script |
| Acceptance oracle, coverage and failure attribution | verification/validation.md |
| Convergence, scaling, initialization and numerical regularization | verification/numerical.md |
| Files needed at use time, final paths and scratch cleanup | delivery/files-and-cleanup.md |
| Promotion rules and ownership itself | this file |

## Promotion test

1. Retain a minimal failing example and actual diagnostics while investigating. Check fixture/oracle validity before attributing a model defect.
2. Identify the causal invariant and applicability boundary. One device's fitted value is not a general rule. A single minimal reproducer can establish a documented parser fact; broader physical generalization needs theory and representative evidence/counterexamples.
3. Choose the smallest scope: device note, family recipe, reusable mechanism or global syntax. Do not promote by keyword or convenience.
4. Reuse an existing rule's owner. If a new mechanism has real cross-family content, create its focused file and one route; do not create empty architectural layers.
5. Verify a discriminating before/after behavior or affected invariant. Documentation-only workflow changes use realistic walkthrough and contradiction review. Expand regression only for actual dependencies/risks.
6. Preserve inheritance/deprecation rationale in the maintaining project's release record, outside the generic skill. Update links and script contracts together.

New rules state:

```text
Applicability:
Correct practice:
Reason / authoritative source or causal evidence:
Discriminating check:
Runtime/version/context (if relevant):
Known counterexample or exclusion:
```

A rule may use concise prose instead of repeating field labels, provided those facts are present. Avoid copied manual catalogs, permanent logs or universal test quotas. If a rule spans topics, put the detailed cause in its owner and link its implications elsewhere. A corpus count or one successful model is not evidence of generality.

## Preserving accumulated experience during restructuring

Read the previous rules and executable helpers before removing or compressing them. In the maintaining project's temporary/release record, map each substantive old clause to its new owner and concrete passage, or record an explicit supersession/rejection reason. A category table, word match or valid link is not semantic proof of inheritance. Preserve the trigger, scope, corrective action and discriminating check; replacing an operational lesson with “check syntax” or “validate carefully” loses it.

Consolidate duplicates into one authoritative rule without deleting distinct conditions or exceptions. Separate obsolete workflow/interface restrictions from the physical, syntax and verification lessons they contain. Verify representative failure scenarios against the revised rules and check for contradictory routes. Do not copy the old package as a second rulebook or require model users to maintain this release-audit ledger.
