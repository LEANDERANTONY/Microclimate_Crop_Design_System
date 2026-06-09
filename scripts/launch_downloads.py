"""Spawn 3 detached parallel raster downloads (one per file) to maximise throughput."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
SCRIPT = os.path.join(HERE, "fetch_safe_rasters.py")
DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

open(os.path.join(ROOT, "data", "raw", "download.log"), "w").close()
for f in ("T_max", "T_mean", "VPD_max"):
    subprocess.Popen([PY, SCRIPT, f], cwd=ROOT, creationflags=DETACHED,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     close_fds=True)
    print("spawned", f)
print("all spawned")
