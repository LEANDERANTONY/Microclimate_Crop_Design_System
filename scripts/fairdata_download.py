"""Authorized downloader for Fairdata IDA / Download service.

Flow (Fairdata download-service): POST /authorize {dataset,file} -> {token};
then GET /download?dataset=&file=&token=  (streamed, resumable).

Usage:
  uv run python scripts/fairdata_download.py --test          # small tile-index file
  uv run python scripts/fairdata_download.py --file "/Tropical_Microclimate/Data_Daily/South_asia/04.tif" --out data/raw/tropmicro/Daily_South_asia_04.tif
"""
import argparse, json, os, time, urllib.request, urllib.error

DSID = "67bdd112-479c-459c-81ce-6e9a2461d954"
BASES = ["https://download.fairdata.fi", "https://download.fairdata.fi/v1"]


def authorize(base, file):
    body = json.dumps({"dataset": DSID, "file": file}).encode()
    req = urllib.request.Request(base + "/authorize", data=body,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "microclimate/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r).get("token")


def get_token(file):
    last = None
    for base in BASES:
        try:
            tok = authorize(base, file)
            if tok:
                return base, tok
        except Exception as e:
            last = f"{base}: {repr(e)[:120]}"
    raise RuntimeError(f"authorize failed ({last})")


def download(file, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    base, tok = get_token(file)
    url = f"{base}/download?dataset={DSID}&file={urllib.parse.quote(file)}&token={tok}"
    have = os.path.getsize(dest) if os.path.exists(dest) else 0
    for attempt in range(1, 20):
        have = os.path.getsize(dest) if os.path.exists(dest) else 0
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "microclimate/1.0",
                                                       "Range": f"bytes={have}-"})
            with urllib.request.urlopen(req, timeout=90) as r, open(dest, "ab") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            break
        except urllib.error.HTTPError as e:
            if e.code == 416:  # already complete
                break
            print(f"  http {e.code}, retry {attempt}"); time.sleep(3)
            base, tok = get_token(file)  # refresh token
            url = f"{base}/download?dataset={DSID}&file={urllib.parse.quote(file)}&token={tok}"
        except Exception as e:
            print(f"  {type(e).__name__}, retry {attempt}"); time.sleep(3)
    return os.path.getsize(dest) if os.path.exists(dest) else 0


if __name__ == "__main__":
    import urllib.parse
    ap = argparse.ArgumentParser()
    ap.add_argument("--file"); ap.add_argument("--out"); ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        f = "/Tropical_Microclimate/Index_map/Tile_Index.shp"
        try:
            base, tok = get_token(f)
            print("AUTHORIZE OK base=", base, "token len=", len(tok) if tok else None)
            n = download(f, "data/raw/tropmicro/Tile_Index.shp")
            print("downloaded bytes:", n)
        except Exception as e:
            print("TEST FAILED:", repr(e)[:200])
    else:
        n = download(a.file, a.out)
        print(f"{a.out}: {n/1e6:.1f} MB")
