"""List files in the Tropical Forest Microclimate Maps dataset via Fairdata/Metax
API, so we can download ONLY the South-India tile instead of the full 38 GB."""
import json, urllib.request

DSID = "67bdd112-479c-459c-81ce-6e9a2461d954"
CANDS = [
    f"https://metax.fairdata.fi/v3/datasets/{DSID}/files?pagination=false",
    f"https://metax.fairdata.fi/v3/files?dataset={DSID}&pagination=false",
    f"https://metax.fairdata.fi/rest/v2/datasets/{DSID}/files",
]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "microclimate/1.0",
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

for url in CANDS:
    print("TRY", url)
    try:
        d = get(url)
        items = d.get("results", d) if isinstance(d, dict) else d
        items = items if isinstance(items, list) else []
        print("  count:", len(items))
        rows = []
        for f in items:
            path = f.get("file_path") or f.get("pathname") or f.get("file_name") or f.get("filename")
            size = f.get("byte_size") or f.get("size") or f.get("file_size")
            rows.append((path, size))
        json.dump(rows, open("data/raw/tropmicro_files.json", "w"))
        # print data tiles (exclude the big sensor-CSV list under Codes/06SLOCV)
        print("\n-- DATA TILES (non-Codes) --")
        for path, size in rows:
            if "/Codes/" not in path:
                print(f"   {size/1e6:8.1f} MB  {path}")
        print("\n-- folders seen --")
        import os as _os
        folders = sorted({_os.path.dirname(p) for p, _ in rows})
        for fo in folders:
            print("   ", fo)
        break
    except Exception as e:
        print("  ERR", repr(e)[:160])
