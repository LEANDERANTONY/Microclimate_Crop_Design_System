# Sensitivity: does the uncertain coconut temperature offset change the decision?

**Question.** The model flags the under-coconut temperature offset as LOW confidence
(extrapolation, ADR-007/008). Everything else under coconut — shade (Beer–Lambert),
wind (shelterbelt), humidity — is physics/known. Does the temperature uncertainty
change *which* intercrops are best at Anaikadu, or only their absolute scores?

**Method.** `scripts/sensitivity_coconut.py`: hold shade/wind/RH fixed at the predicted
coconut-wide values for the real Anaikadu site (ERA5 2019 + SoilGrids), sweep ONLY the
under-canopy temperature across its plausible band, and re-rank the intercrops.

**Result (viability, 0–100).**

| scenario | under-canopy t_max | top crops |
|---|---|---|
| cooler −3 °C | 34.1 | Nutmeg(100), Banana(63), Black pepper(48) |
| cooler −1.5 °C | 35.6 | Nutmeg(78), Banana(39), Black pepper(37) |
| model median | 37.1 | Nutmeg(28), Black pepper(27), Banana(14) |
| warmer +1.5 °C | 38.6 | Black pepper(14), others ~0 |
| warmer +3 °C | 40.1 | all ~0 (temperature-limited) |

The model's own dT_max 80% band is wide: **[−1.9, +7.6] °C** (under-canopy t_max ~32–42).

**Findings.**

1. **Shortlist is robust.** Whenever anything is viable, the candidates are always
   **nutmeg, black pepper, banana**; cocoa/vanilla/ginger/pomegranate are never
   competitive. So *which* crops to trial does **not** depend on the pending data.
2. **Viability level is sensitive.** Anaikadu is hot and these crops are
   temperature-limited, so the offset controls whether they thrive (cool end) or
   collapse (hot end).
3. **Physics favours the cooler end.** The ML median offset under coconut is unreliable
   (coconut now resembles the open-palm training regime, predicting ~no cooling), while
   the shade physics (~39% light reduction) implies real cooling. The realistic case is
   the cool-to-median range, where the shortlist is viable.

**Decision implication.** Commit to the **nutmeg / pepper / banana** shortlist now — no
need to wait. The pending regional data / a season of on-plot sensing refines *how well*
they perform, not *what* to plant. This is exactly the layer the year-1 logger tightens.
