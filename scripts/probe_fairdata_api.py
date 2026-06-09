"""Probe the Fairdata download-service API to learn the real authorize/download flow."""
import json, urllib.request, urllib.error

DSID = "67bdd112-479c-459c-81ce-6e9a2461d954"
F = "/Tropical_Microclimate/Index_map/Tile_Index.shp"
B = "https://download.fairdata.fi"


def show(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    hdrs = {"User-Agent": "microclimate/1.0", "Accept": "application/json"}
    if data: hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            txt = r.read(2000).decode("utf-8", "replace")
            print(f"{method} {url} [{r.status}] -> {txt[:500]}")
    except urllib.error.HTTPError as e:
        print(f"{method} {url} [{e.code}] -> {e.read(800).decode('utf-8','replace')[:500]}")
    except Exception as e:
        print(f"{method} {url} ERR {repr(e)[:150]}")


show("GET", f"{B}/requests?dataset={DSID}")
show("POST", f"{B}/authorize", {"dataset": DSID, "file": F})
show("POST", f"{B}/requests", {"dataset": DSID, "scope": [F]})
show("GET", f"{B}/requests?dataset={DSID}")
