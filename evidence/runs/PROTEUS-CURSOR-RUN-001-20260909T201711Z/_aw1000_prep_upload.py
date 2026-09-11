"""Scan + base64 AW1000 carrier; patch secret_refs annotations."""
from __future__ import annotations

import base64
import json
import re
import zipfile
from pathlib import Path

EV = Path(r"C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z")
ZIP = EV / "drive_carrier_entity.router.aw1000.home.zip"
WORLD = EV / "world_memory_home" / "world" / "entities" / "entity.router.aw1000.home"

# Patch secret refs
sr_path = WORLD / "secret_refs.json"
data = json.loads(sr_path.read_text(encoding="utf-8"))
for r in data["secret_refs"]:
    r["plaintext"] = None
    if r["secret_uri"] == "secret://router.aw1000.home.admin":
        r["AW1000_REAL_SECRET"] = "UNAVAILABLE"
        r["external_pointer"] = r"C:\projects\aw1000-audit\askpass.cmd"
        r["external_pointer_read"] = False
        r["note"] = (
            "askpass.cmd exists but was not read; plaintext never loaded into "
            "broker or entity memory this episode"
        )
sr_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

# Re-export after patch
import os
import sys

sys.path.insert(0, r"C:\projects\Proteus\src")
os.environ["AIYE_HOME"] = str(EV / "world_memory_home")
os.environ["PROTEUS_WORLD_ROOT"] = str(EV / "world_memory_home" / "world")
os.environ["PROTEUS_HOME"] = str(EV / "world_memory_proteus_home")
from proteus.world import export_entity_carrier_bundle

meta = export_entity_carrier_bundle(
    "entity.router.aw1000.home", out_path=ZIP
)
meta.pop("payload", None)

bad = []
with zipfile.ZipFile(ZIP) as zf:
    for n in zf.namelist():
        text = zf.read(n).decode("utf-8", "replace")
        if re.search(r'"plaintext"\s*:\s*"[^"]+"', text):
            bad.append(("plaintext_value", n))
        if "SYNTHETIC-AW1000-BROKER" in text:
            bad.append(("synth_leak", n))
        if "BEGIN OPENSSH PRIVATE KEY" in text or "BEGIN RSA PRIVATE KEY" in text:
            bad.append(("private_key", n))
print("SCAN", bad or "CLEAN")
print("META", json.dumps(meta, indent=2))
b64 = base64.b64encode(ZIP.read_bytes()).decode("ascii")
(EV / "drive_carrier_aw1000.b64.txt").write_text(b64, encoding="ascii")
print("B64_LEN", len(b64))
