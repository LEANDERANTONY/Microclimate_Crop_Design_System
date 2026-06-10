"""QA audit of every crop's economic inputs: surface gross/cost/net and standalone
finance (ideal suitability) so implausible numbers stand out for cross-checking."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from agroforestry.economics import CROP_ECON
from agroforestry.finance import CROP_FIN, crop_cashflow, npv, irr, payback


def money(x):
    return f"{x/1000:>8,.0f}k"


print("Per-crop economic audit (ideal suitability growth=100, disease=0)\n")
print(f"{'crop':13s} {'yield_c':>8s} {'price_mid':>9s} {'gross':>9s} {'cost':>8s} {'net':>9s} "
      f"{'g/cost':>6s} | {'estab':>7s} {'gest':>4s} {'NPV':>9s} {'IRR':>5s} {'payb':>5s}")
for crop, e in CROP_ECON.items():
    ylo, yc, yhi = e["yield"]; plo, phi = e["price"]; cost = e["cost"]
    pmid = (plo + phi) / 2
    gross = yc * pmid
    net = gross - cost
    fin = CROP_FIN[crop]
    cf = crop_cashflow(crop, 100, 0)        # ideal monocrop
    r = irr(cf); pb = payback(cf)
    rs = f"{r*100:.0f}%" if r is not None else "n/a"
    pbs = f"{pb}y" if pb else "nevr"
    print(f"{crop:13s} {yc:8.0f} {pmid:9.1f} {money(gross)} {money(cost)} {money(net)} "
          f"{gross/cost:6.1f} | {fin['establish']/1000:6.0f}k {fin['gestation']:4d} "
          f"{money(npv(cf))} {rs:>5s} {pbs:>5s}")

print("\nFlags to check: net <=0 at IDEAL suitability (cost too high / yield-price too low);")
print("g/cost <1.5 (thin margin -> likely cost overstated); IRR n/a or payback never;")
print("gestation/establish that look wrong for the crop.")
