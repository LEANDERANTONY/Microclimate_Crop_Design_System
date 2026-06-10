# Roadmap

Build priorities for the agroforestry microclimate → crop → profit system.
Philosophy unchanged: build what the available data can honestly support, defer
what it cannot, label confidence everywhere.

## Done (all six layers built, validated, runnable — 26 tests)

- **Repo**: `uv` env + lockfile, `src/` package, ADRs 001–013, DEVLOG, tests.
- **Layer 1 — microclimate**: Beer–Lambert light + shelterbelt wind (physics);
  XGBoost quantile temp/VPD offsets + conformal intervals; **OOD flag** (ADR-007);
  design→feature mapping grounded on real TN satellite values (ADR-013).
- **Real data integrated**: SAFE Borneo + La Jarda Spain forest loggers (two
  macroclimates) + SAFE oil-palm rasters (open-canopy regime). Earth Engine features
  (ERA5, SoilGrids, DEM, MODIS, ETH canopy). Ambient-reference fix (ERA5 atmospheric) ADR-006.
- **Transfer validated honestly (ADR-012)**: skill-scored LOSO (within-climate dT_mean
  +27% skill, MAE 0.28–0.33 °C) **and** leave-one-CLIMATE-out (cross-climate skill goes
  negative on a held-out climate; intervals lose calibration). A physics-prior+residual
  **hybrid** was built + tested — competitive in-distribution, does NOT rescue cross-climate;
  pure quantile model stays default. `scripts/run_validation.py` → loso/loco_metrics.json.
- **Layer 2 — disease**: two axes (foliar air + soil-water/waterlogging), variety
  susceptibility, drainage lever; literature-calibrated (ADR-003/004), waterlogging
  data-calibrated (ADR-005).
- **Layer 3 — suitability**: fuzzy limiting-factor `viability()`.
- **Layer 4 — economics**: yield × growth × (1−disease) × banded price − validated cost;
  coconut + timber overstorey; costs validated vs NHB DPRs/TNAU, prices vs live Agmarknet
  (ADR-010/011, `reports/economics_qa.md`).
- **Layer 5 — finance**: 25-yr cash-flow with gestation/bearing/harvest timing; NPV/IRR/payback.
- **Layer 6 — uncertainty**: Monte Carlo → NPV distribution + P(loss).
- **Inverse design**: profit objective over overstorey/canopy/windbreak/drainage.
- **Real-site application**: Anaikadu (GD Home Stay pin) end-to-end; sensitivity shows the
  intercrop shortlist is robust to the temperature uncertainty.
- **Deliverables**: interactive preprint report (`reports/anaikadu_preprint.html`),
  README with figures, reproducible `export_results.py` → `make_figures.py` / `build_dashboard.py`.

## Next: firm the two soft layers with data (not blocking)

- **Temperature offset under coconut** (currently extrapolation): the leave-one-climate-out
  test (ADR-012) showed neither the tree nor the physics-prior hybrid transfers to a
  held-out climate, so the fix is **data, not a cleverer model** — add a palm/open-canopy
  or warm-night-tropical training source: SoilTemp raw loggers (request emailed) and/or
  the pan-tropical understory maps (30 m South-Asia subset requested from authors). With
  a warm-climate source in-set, the hybrid's backbone would interpolate rather than
  extrapolate. The definitive fix is the user's **own plot logger (year 1)** — a single
  season would collapse the offset uncertainty (ADR-008/009/012). Also: per-climate
  (Mondrian) conformal calibration to restore out-of-climate interval coverage.
- **Economics prices to HIGH**: CEDA-Ashoka 3-yr monthly Agmarknet series (site is
  bot-blocked from this environment → user-side CSV export), plus TNAU per-crop cost line
  items for the high-input crops.

## Later: depth + write-up

- **Written manuscript** from the preprint sections (publication/preprint target).
- **Multi-crop portfolio** optimisation (a mix, not one intercrop) and a **spatial planting
  layout** (windbreak placement, row design).
- Bayesian-opt / NSGA-II inverse design replacing the grid search.
- Disease parameters fitted to observed incidence once field data exists; hourly
  leaf-wetness model; coastal salinity axis (flagged ADR-005).

## Future research extensions

- Physics-informed (PINN) coupled energy/water balance once data justifies it.
- Spatial (GNN) within-field microclimate gradients if multi-node sensing arrives.
