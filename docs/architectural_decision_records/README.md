# Architectural Decision Records

Short, dated records of significant, hard-to-reverse decisions. Each ADR states
the context, the decision, and its consequences. ADRs are append-only — to
change a decision, write a new ADR that supersedes the old one.

| ADR | Title | Status |
|---|---|---|
| [001](ADR-001-offset-and-physics.md) | Decompose into layers; predict offsets; physics-first | Accepted |
| [002](ADR-002-disease-layer.md) | Add a mechanistic disease layer between microclimate and viability | Accepted |
| [003](ADR-003-sourced-calibration.md) | Apply literature-sourced envelopes and disease parameters | Accepted |
| [004](ADR-004-soil-water-axis.md) | Two-axis disease model: separate soil-water axis from air microclimate | Accepted |
| [005](ADR-005-waterlogging-calibration.md) | Data-calibrated seasonal waterlogging index (SoilGrids + CGWB) | Accepted |
| [006](ADR-006-real-data-safe.md) | First real-data integration: SAFE Project (Borneo) microclimate via Earth Engine | Accepted |
| [007](ADR-007-ood-extrapolation.md) | Out-of-distribution flag for off-canopy-type designs (coconut) | Accepted |
| [008](ADR-008-oilpalm-open-canopy-regime.md) | Add SAFE oil-palm open-canopy regime; OOD is macro-driven | Accepted |
| [009](ADR-009-regional-transfer-data.md) | Source regional data to narrow the Borneo/Spain transfer gap | Accepted |
| [010](ADR-010-coconut-economics-qa.md) | Coconut economics QA: gestation-cost bug fix | Accepted |
| [011](ADR-011-crop-cost-validation.md) | Validate/reconcile per-crop costs vs NHB DPRs / TNAU | Accepted |
| [012](ADR-012-transfer-validation-and-hybrid.md) | Skill-scored LOSO/LOCO transfer validation + physics-guided hybrid (tested) | Accepted |
| [013](ADR-013-grounded-design-features.md) | Ground design→feature mapping with real TN satellite features | Accepted |
| [014](ADR-014-model-benchmark-and-fewshot-conformal.md) | Model-family benchmark; keep XGBoost (GP as transfer-honest reference); few-shot conformal recalibration | Accepted |
| [015](ADR-015-modular-publication-program.md) | Split into modular three-paper program; non-destructive monorepo; pre-register external validation | Accepted |
