"""Probe the data.gov.in Agmarknet (mandi price) API: confirm field names + coverage."""
import json, urllib.parse, urllib.request

KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"  # public demo key
RES = "9ef84268-d588-465a-a308-a864a43d0070"  # Current Daily Mandi Prices


def q(params):
    url = f"https://api.data.gov.in/resource/{RES}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "microclimate/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


# 1) unfiltered sample to learn field names
d = q({"api-key": KEY, "format": "json", "limit": 1})
print("total records in resource:", d.get("total"))
recs = d.get("records", [])
if recs:
    print("FIELDS:", list(recs[0].keys()))
    print("sample:", recs[0])

# 2) try a TN + commodity filter (field names guessed; adjust after seeing FIELDS)
for fld in ("State", "state"):
    try:
        d2 = q({"api-key": KEY, "format": "json", "limit": 5,
                f"filters[{fld}]": "Tamil Nadu", "filters[Commodity]": "Banana"})
        print(f"\nfilter[{fld}]=Tamil Nadu, Commodity=Banana -> count {d2.get('count')}, total {d2.get('total')}")
        for rr in d2.get("records", [])[:3]:
            print("  ", {k: rr.get(k) for k in rr})
        break
    except Exception as e:
        print(f"filter[{fld}] err", repr(e)[:120])
