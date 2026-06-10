# Roadmap

Build priorities for the agroforestry microclimate → crop → profit system.
Philosophy unchanged: build what the available data can honestly support, defer
what it cannot, label confidence everywhere.

## Done (all six layers built, validated, runnable — 22 tests)

- **Repo**: `uv` env + lockfile, `src/` package, ADRs 001–011, DEVLOG, tests.
- **Layer 1 — microclimate**: Beer–Lambert light + shelterbelt wind (physics);
  XGBoost quantile temp/VPD offsets + conformal intervals; **OOD flag** (ADR-007).
- **Real data integrated**: SAFE Borneo + La Jarda Spain forest loggers (two
  macroclimates) + SAFE oil-palm rasters (open-canopy regime). Earth Engine features
  (ERA5, SoilGrids, DEM, MODIS, ETH canopy). **Cross-macroclimate transfer demonstrated:
  LOSO dT_mean MAE 0.28 °C** (ADR-006). Ambient-reference fix (ERA5 atmospheric) ADR-006.
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

- **Temperature offset under coconut** (currently extrapolation): add a palm/open-canopy
  or warm-night-tropical training source — SoilTemp raw loggers (request emailed) and/or
  the pan-tropical understory maps (30 m South-Asia subset requested from authors). The
  definitive fix is the user's **own plot logger (year 1)** — a single season would
  collapse the offset uncertainty (ADR-008/009).
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
