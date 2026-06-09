"""Download the SAFE landscape microclimate rasters (Zenodo 7893600), resumable.

Modelled daily projections (Jucker/Hardwick lineage) of sub-canopy T_max, T_mean,
VPD_max at 50 m over the SAFE landscape, Borneo -- includes oil-palm plantation,
the open-canopy regime missing from our forest training. VPD_mean is not needed.

Resumable via HTTP Range; verifies against known sizes; logs to data/raw/download.log.
"""
import os
import time
import urllib.request

BASE = "https://zenodo.org/records/7893600/files/{}.tif?download=1"
# md5-listed sizes from the Zenodo record (bytes).
EXPECTED = {
    "T_max": 359_800_000,
    "T_mean": 387_600_000,
    "VPD_max": 421_000_000,
}
OUT = "data/raw"
LOG = os.path.join(OUT, "download.log")
os.makedirs(OUT, exist_ok=True)


def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def fetch(name):
    dest = os.path.join(OUT, name + ".tif")
    exp = EXPECTED[name]
    have = os.path.getsize(dest) if os.path.exists(dest) else 0
    if have >= exp * 0.99:
        log(f"OK {name}: {have/1e6:.1f} MB (complete)")
        return
    # resume
    for attempt in range(1, 30):
        have = os.path.getsize(dest) if os.path.exists(dest) else 0
        if have >= exp * 0.99:
            break
        req = urllib.request.Request(BASE.format(name), headers={"Range": f"bytes={have}-"})
        try:
            log(f"GET {name} from byte {have} (attempt {attempt})")
            with urllib.request.urlopen(req, timeout=60) as r, open(dest, "ab") as out:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
        except Exception as e:
            log(f"  retry {name}: {type(e).__name__} {str(e)[:80]}")
            time.sleep(3)
    have = os.path.getsize(dest) if os.path.exists(dest) else 0
    log(f"DONE {name}: {have/1e6:.1f} MB")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:        # single file (for parallel downloads)
        fetch(sys.argv[1])
    else:
        for n in EXPECTED:
            fetch(n)
        log("ALL DONE")
