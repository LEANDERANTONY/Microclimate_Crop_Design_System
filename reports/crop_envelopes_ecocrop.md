# Headline-crop envelopes — authoritative sourcing (ECOCROP / PROSEA)

Tightened the growth envelopes for the two **recommended** intercrops against
authoritative references, so the headline recommendation does not rest on
extension-blog values. Verified June 2026. The other crops in `config.CROPS`
remain screening-grade (horticultural/extension sources) — flagged for later.

## Black pepper — *Piper nigrum* (FAO ECOCROP, code 1714)

Source: FAO ECOCROP data sheet, https://ecocrop.apps.fao.org/ecocrop/srv/en/dataSheet?id=1714
(and crop view id=1714).

| Variable | ECOCROP | Encoded in `config.CROPS["Black pepper"]` |
|---|---|---|
| Temperature | optimal **22–35 °C**, absolute **10–40 °C** | `t = [22, 35, 10, 40]` |
| Relative humidity | thrives **65–95 %** (crop view narrative) | `rh = [65, 90, 50, 100]` |
| Light | "clear skies → light shade" (tolerates low–moderate shade) | `shade = [20, 50, 5, 70]` |
| Rainfall | optimal 2500–4000 mm, absolute 2000–5500 mm | not in envelope (irrigation-controlled) |
| Altitude / latitude | best < 500 m; 15–20° of equator | site context (Anaikadu OK) |
| Note | ECOCROP explicitly lists pepper as a **useful agroforestry species** | supports the coconut-intercrop framing |

Change vs previous: optimal upper raised 32 → **35 °C** and RH lower 60 → **65 %**,
both to match ECOCROP exactly. The higher optimal-max slightly improves pepper's
growth score at hot Anaikadu (mean T_max ≈ 34 °C now sits at the top of the optimal
band rather than just outside it) — a more defensible, source-backed envelope.

## Nutmeg — *Myristica fragrans* (PROSEA; ECOCROP-consistent)

Sources: PROSEA (Pl@ntUse, *Myristica fragrans*); FAO crop-information notes; converged
secondary references. (The ECOCROP numeric sheet for nutmeg was not cleanly retrievable
in this session — a search hit mis-resolved to *Malus domestica*, id 1407 — so values are
taken from PROSEA, a standard authoritative compendium, pending a direct ECOCROP id check.)

| Variable | PROSEA / refs | Encoded in `config.CROPS["Nutmeg"]` |
|---|---|---|
| Temperature | warm humid tropics, mean **25–30 °C**; **flowering impaired > 35 °C** and by hot dry winds; absolute ≈ **20–38 °C** | `t = [25, 32, 20, 38]` |
| Rainfall | **2000–3500 mm**, no real dry period (dry spell can induce flowering) | not in envelope (irrigation) |
| Shade | **shade-demanding**, especially juvenile | `shade = [25, 50, 10, 65]` |
| Altitude | best **< 700 m**; shallow roots → wind-sensitive | `wind = [1.5, 3.0]` (low tolerance) |
| Waterlogging | grows on most soils **without waterlogging risk** | handled on the soil-water disease axis |

Change vs previous: optimal upper tightened 35 → **32 °C** to reflect that flowering is
impaired above ~35 °C (the previous 35 °C optimal-max was too generous for the
reproductive stage that actually sets yield).

## Disease parameters

The mechanistic disease parameters (`config.DISEASES`) for these crops — pepper
**foot rot** (*Phytophthora capsici*, soil-water axis) and the foliar set — remain
literature-shaped (ADR-003) and are not changed here; they are confidence-flagged
MODERATE and slated for incidence calibration with field data. This pass tightened the
**growth envelopes** only.
