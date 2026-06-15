# Docs map & maintenance contract

How the project's documentation is organised and **how to keep it clean**. If you are an
agent or collaborator making a change, follow the "When you change X, update Y" rules below
so the docs never drift from the code.

## Where things live

### Repo root (tracked)
| File | Purpose | Update cadence |
|---|---|---|
| `README.md` | Public showcase: what the system does, key findings, how to run, layout. | When the public story / headline results / run commands change. |
| `ROADMAP.md` | Build priorities and what's next (incl. the publication program). | When priorities or stage status change. |
| `DEVLOG.md` | Chronological build log, **newest first**. | Append an entry after any meaningful change. |
| `folder_structure.txt` | Flat tree of the repo. | When directories are added/removed. |

### `docs/` (tracked)
| File | Purpose | Update cadence |
|---|---|---|
| `architecture.md` | The six-layer system design + validation + publication structure. | When a layer's method, the validation protocol, or the module map changes. |
| `modeling_blueprint.md` | The modelling rationale (which model for which sub-problem). | When the modelling approach changes. |
| `economics_layer.md` | Economics/finance assumptions and staging. | When economics inputs/assumptions change. |
| `data_acquisition.md` | Data sources and how they're assembled. | When a data source is added/changed. |
| `external_validation_datasets.md` | Register of held-out validation datasets + the pre-registration / independence rule. | When a validation dataset is added, acquired, or its status changes. |
| `architectural_decision_records/` | One ADR per significant, hard-to-reverse decision (append-only). | Write a **new** ADR for each significant decision; never rewrite an accepted one. |
| `architectural_decision_records/README.md` | The ADR index table. | Add a row whenever a new ADR is created. |

### Local-only (gitignored — **not** on GitHub)
Operator briefings and working drafts are kept local for privacy and are **not** version-
controlled: `AGENTS.md` (single cold-start briefing for agents) and `docs/PROJECT_CONTEXT.md`
(durable Cowork context), plus any working drafts and outreach kept under gitignored paths.
The full local-only map lives in **`AGENTS.md`** (read it first when picking the project up).
Keep these current the same way as the tracked docs, but they stay on disk only.

## "When you change X, update Y"

- **Code / a layer's method** → update `architecture.md` (and `modeling_blueprint.md` if the
  approach changed); append `DEVLOG.md`.
- **A significant or hard-to-reverse decision** → write a new **ADR**, add it to the ADR
  index, and reference it from the relevant doc + `DEVLOG.md`.
- **Validation data** (new dataset, acquisition, status) → update
  `external_validation_datasets.md`; cite the governing ADR.
- **Priorities / what's next** → update `ROADMAP.md`.
- **Anything meaningful** → append `DEVLOG.md` (newest first) and refresh the dated
  "current state" snapshot in `AGENTS.md` / `PROJECT_CONTEXT.md` (local).
- **New directory** → update `folder_structure.txt` and the layout in `README.md`.

## House rules

- ADRs are **append-only**: to change a decision, write a new ADR that supersedes the old one.
- Keep **confidence labels** load-bearing in any doc that reports results (physics HIGH,
  learned offset MODERATE/OOD-flagged, etc.) — see `architecture.md` and the ADRs.
- Point-in-time facts (test counts, metric values, dated snapshots) live mainly in the
  `AGENTS.md` / `PROJECT_CONTEXT.md` snapshot and `DEVLOG.md`; the durable docs should avoid
  hard-coding numbers that go stale.
- Don't put private/working content (drafts, correspondence, personal site detail beyond
  what `README.md` already states) into tracked docs.
