"""Synthetic 'borrowed-label' dataset -- realistic stress-test version.

Designed to make the pipeline EARN its metrics, mimicking the messiness of real
sub-canopy microclimate data:

  * Site-clustered macroclimate -- each site has a coherent climate regime
    (elevation sets a lapse-rate temperature, a rainfall/humidity regime, a
    species-like canopy-height slope). Macro features are NOT i.i.d. per row.
  * Correlated features -- solar/temp/RH/diurnal-range move together via a
    seasonal phase; NDVI/FAPAR follow canopy cover.
  * Non-linear offsets with interactions -- canopy buffering saturates with LAI,
    is magnified on hot/sunny days (De Frenne: buffering grows at extremes),
    and is eroded by wind mixing. XGBoost has to find these, not a line.
  * Heteroscedastic noise -- sparser canopy and higher VPD are noisier, which
    stresses the quantile + conformal intervals.
  * Shared unobserved site latent -- one hidden 'site quirk' drives correlated
    offsets; never given to the model, so leave-one-site-out reports an honest
    transfer gap.
  * Deliberately weak features (slope, soc) -- near-irrelevant, so feature
    importance / pruning is a real test.

Columns are identical to data_load.py output, so swapping to real data changes
nothing downstream.
"""
import numpy as np
import pandas as pd
from agroforestry.config import RAW_FEATURES, TARGETS, GROUP_COL

K_EXT = 0.55  # nominal extinction coefficient used for the 'true' cover


def _tetens_es(t):
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def make_dataset(n_sites=60, reps_per_site=40, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for s in range(n_sites):
        # ---- site-level climate regime (gives spatial structure) ----
        elevation = rng.uniform(0, 1500)
        temp_base = 30.0 - 0.0055 * elevation + rng.normal(0, 1.2)   # lapse rate
        rain_regime = rng.uniform(900, 3500)
        rh_base = np.clip(60 + 0.006 * rain_regime + rng.normal(0, 4), 55, 90)
        height_slope = rng.uniform(3, 7)        # species-like canopy-height per LAI
        twi = rng.uniform(3, 12)                # site-level, weak real effect on dVPD
        clay = rng.uniform(10, 60)              # site-level, weak real effect on dT_max
        site_latent = rng.normal(0, 1)          # UNOBSERVED quirk -> drives LOSO gap

        for _ in range(reps_per_site):
            # ---- seasonal phase ties solar/temp/RH together ----
            phase = rng.uniform(0, 2 * np.pi)
            solar = float(np.clip(22 + 5 * np.sin(phase) + rng.normal(0, 1.5), 12, 28))
            t_mean = temp_base + 2.5 * np.sin(phase) + rng.normal(0, 0.8)
            diurnal = np.clip(8 + 0.6 * (solar - 22) - 0.04 * (rh_base - 70)
                              + rng.normal(0, 1.0), 4, 18)
            t_max = t_mean + diurnal / 2
            t_min = t_mean - diurnal / 2
            rh = float(np.clip(rh_base - 1.5 * (solar - 22) + rng.normal(0, 4), 40, 98))
            wind = float(np.clip(rng.lognormal(mean=np.log(2.5), sigma=0.5), 0.3, 10))
            rainfall = float(rain_regime + rng.normal(0, 150))

            # ---- canopy (LAI varies by management/season; height site-flavoured) ----
            lai = float(np.clip(rng.uniform(0.2, 4.0) + 0.2 * np.sin(phase), 0.1, 4.2))
            cover = 1 - np.exp(-K_EXT * lai)
            canopy_height = max(0.5, 2 + lai * height_slope + rng.normal(0, 1))
            ndvi = float(np.clip(0.3 + 0.6 * cover + rng.normal(0, 0.05), 0, 1))
            fapar = float(np.clip(0.9 * cover + rng.normal(0, 0.05), 0, 1))

            # genuinely irrelevant per-row features (should rank at the bottom of
            # importance -- they never enter any target)
            slope = rng.uniform(0, 25)
            soc = rng.uniform(5, 40)

            es = float(_tetens_es(t_max))
            vpd_amb = es * (1 - rh / 100)
            hot = max(t_max - 30, 0)              # extremity term

            # ---- non-linear buffering with interactions ----
            # stronger when hot & sunny, weaker when windy; saturates via cover
            buff = cover * (1 + 0.25 * hot) * (0.7 + 0.3 * solar / 22) / (1 + 0.15 * wind)
            dT_max = (-3.2 * buff
                      + 0.012 * canopy_height
                      + 0.004 * clay              # mild thermal inertia (weak)
                      + 0.8 * site_latent
                      + rng.normal(0, 0.3 + 0.5 * (1 - cover)))     # heteroscedastic

            dT_mean = (-1.0 * cover * (0.8 + 0.2 * solar / 22)
                       + 0.35 * site_latent
                       + rng.normal(0, 0.2 + 0.3 * (1 - cover)))

            dVPD = (-0.5 * cover * vpd_amb / (1 + 0.1 * wind)
                    - 0.02 * (twi - 7)            # wetter sites buffer VPD a bit (weak)
                    + 0.08 * site_latent
                    + rng.normal(0, 0.1 + 0.15 * vpd_amb * (1 - cover)))

            rows.append(dict(
                site_id=s, t_mean=t_mean, t_max=t_max, t_min=t_min, rh=rh,
                wind=wind, solar=solar, rainfall=rainfall, lai=lai,
                canopy_height=canopy_height, ndvi=ndvi, fapar=fapar,
                elevation=elevation, slope=slope, twi=twi, soc=soc, clay=clay,
                dT_max=dT_max, dT_mean=dT_mean, dVPD=dVPD,
            ))

    df = pd.DataFrame(rows)
    missing = set(RAW_FEATURES + TARGETS + [GROUP_COL]) - set(df.columns)
    assert not missing, f"synthetic data missing columns: {missing}"
    return df


if __name__ == "__main__":
    d = make_dataset()
    print(d.shape)
    print(d.describe().round(2).T[["mean", "std", "min", "max"]])
