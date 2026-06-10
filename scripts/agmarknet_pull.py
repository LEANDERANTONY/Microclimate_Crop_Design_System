"""Pull live Tamil Nadu mandi prices (data.gov.in Agmarknet feed) for our crops.
The API serves the CURRENT daily snapshot (not history), so this gives a real
present-day price band across TN markets; multi-year context stays from the sourced doc.
Prices are Rs/quintal -> converted to Rs/kg (/100)."""
import json, statistics, urllib.parse, urllib.request

KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
RES = "9ef84268-d588-465a-a308-a864a43d0070"
COMMS = ["Banana", "Pomegranate", "Ginger(Green)", "Mango", "Guava", "Grapes",
         "Black pepper", "Coconut", "Dry Ginger", "Amla(Nelli Kai)", "Papaya"]


def q(params):
    url = f"https://api.data.gov.in/resource/{RES}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mc/1.0"}), timeout=40) as r:
        return json.load(r)


def stats_for(commodity, state="Tamil Nadu"):
    d = q({"api-key": KEY, "format": "json", "limit": 2000,
           "filters[state]": state, "filters[commodity]": commodity})
    recs = d.get("records", [])
    if not recs and state:                      # fall back to national if no TN rows today
        d = q({"api-key": KEY, "format": "json", "limit": 2000, "filters[commodity]": commodity})
        recs = d.get("records", [])
        state = "All-India"
    modal = [float(r["modal_price"]) / 100 for r in recs if r.get("modal_price")]  # Rs/kg
    if not modal:
        return None
    modal.sort()
    n = len(modal)
    pct = lambda p: modal[min(n - 1, int(p * n))]
    return {"n": n, "scope": state, "min": modal[0], "p25": pct(.25), "median": pct(.5),
            "p75": pct(.75), "max": modal[-1], "markets": len({r.get("market") for r in recs})}


print("Live Agmarknet snapshot (data.gov.in) -- Rs/kg modal across markets\n")
print(f"{'commodity':16s} {'scope':10s} {'n':>4s} {'mkts':>4s} {'min':>7s} {'p25':>7s} {'median':>7s} {'p75':>7s} {'max':>7s}")
for c in COMMS:
    try:
        s = stats_for(c)
        if s:
            print(f"{c:16s} {s['scope']:10s} {s['n']:4d} {s['markets']:4d} "
                  f"{s['min']:7.1f} {s['p25']:7.1f} {s['median']:7.1f} {s['p75']:7.1f} {s['max']:7.1f}")
        else:
            print(f"{c:16s} -- no records today")
    except Exception as e:
        print(f"{c:16s} ERR {repr(e)[:80]}")
print("\nNote: single-day snapshot (API has no history). Coconut Agmarknet unit varies")
print("(often Rs/100 nuts or Rs/quintal) -- cross-check before use. 3-yr series = CEDA bulk.")
