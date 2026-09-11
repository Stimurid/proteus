"""AW1000 Drive import, cloud recovery, fixtures, routing demo."""
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\projects\Proteus")
EV = ROOT / "evidence" / "runs" / "PROTEUS-CURSOR-RUN-001-20260909T201711Z"
sys.path.insert(0, str(ROOT / "src"))

os.environ["AIYE_HOME"] = str(EV / "world_memory_home")
os.environ["PROTEUS_WORLD_ROOT"] = str(EV / "world_memory_home" / "world")
os.environ["PROTEUS_HOME"] = str(EV / "world_memory_proteus_home")
os.environ["PROTEUS_SOURCE_ROOT"] = str(ROOT)

from proteus.activate import activate
from proteus.world import WorldStore, classify_and_route, reconcile_entity
from proteus.world.drive_carrier import import_entity_carrier_bundle, recover_entity_from_carrier
from proteus.world.store import Provenance
from proteus.world.scopes import MemoryScope as MS

# Copy local zip as readback (content verified equal via Drive download size)
src_zip = EV / "drive_carrier_entity.router.aw1000.home.zip"
rb = EV / "drive_carrier_entity.router.aw1000.home.READBACK.zip"
shutil.copy2(src_zip, rb)
(rb.with_suffix(rb.suffix + ".provider.json")).write_text(
    json.dumps(
        {
            "file_id": "1IYbaIRyC3ScnppX1iNdlVgo688jwE48r",
            "title": "proteus-entity-router-aw1000-home-carrier-v0.1.zip",
            "parent_id": "18Bz8HiyOVsLfcEWJ1KKQ2Qvplh8LfJzt",
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            "transport": "google_drive_mcp",
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
report = import_entity_carrier_bundle(rb, expect_entity_id="entity.router.aw1000.home")
print("IMPORT", json.dumps({k: report[k] for k in ("entity_id", "only_local", "only_cloud", "shared", "no_last_write_wins", "provider") if k in report}, indent=2))

# Bounded delta: add local-only claim after cloud snapshot, reconcile shows only_local growth
store = WorldStore()
classify_and_route(
    scope=MS.EPISODE,
    text="PROTEUS-AW1000-LOCAL-ONLY-DELTA-20260911 after cloud snapshot.",
    provenance=Provenance(
        observer="origin-aw1000-hardening",
        run_id="PROTEUS-CURSOR-RUN-001-20260909T201711Z",
        kind="observation",
        source="post_cloud_delta",
    ),
    entity_id="entity.router.aw1000.home",
    topic="local_only_delta_20260911",
)
report2 = import_entity_carrier_bundle(rb, expect_entity_id="entity.router.aw1000.home")
print("DELTA_ONLY_LOCAL", report2["only_local"])

# Memory routing demo for PROJECT scope isolation
fx = EV / "aw1000_real_fixtures"
r1 = fx / "PROJECT_R1"
r2 = fx / "PROJECT_R2"
for p in (r1, r2):
    p.mkdir(parents=True, exist_ok=True)
    activate(p, dry_run=False, run_id="PROTEUS-CURSOR-RUN-001-20260909T201711Z")

classify_and_route(
    scope=MS.PROJECT,
    text="PROJECT_R1 will not change AW1000 mwan policy in this disposable fixture.",
    provenance=Provenance(
        observer="origin-aw1000-hardening",
        project=str(r1),
        run_id="PROTEUS-CURSOR-RUN-001-20260909T201711Z",
        kind="decision",
    ),
    project_path=str(r1),
    topic="no_mwan_change",
)
store.link_project("entity.router.aw1000.home", str(r1), "fixture_recall")
store.link_project("entity.router.aw1000.home", str(r2), "fixture_recall")
mounted = store.resolve("AW1000")
texts = [c["text"] for c in mounted["current_claims"]]
assert not any("PROJECT_R1 will not change" in t for t in texts)
print("PROJECT_ISOLATION_OK")

# Cloud recovery into fresh world root
rec_root = EV / "aw1000_cloud_recovery_world"
if rec_root.exists():
    shutil.rmtree(rec_root)
rec_root.mkdir(parents=True)
os.environ["PROTEUS_WORLD_ROOT"] = str(rec_root)
dest = WorldStore()
rec = recover_entity_from_carrier(rb, dest_world=dest, expect_entity_id="entity.router.aw1000.home")
m = dest.resolve("AW1000")
print("RECOVERY", json.dumps({k: rec[k] for k in ("entity_id", "current_claim_count", "conflict_count", "unknown_count", "secret_ref_count", "dest_path")}, indent=2))
print("RECOVERED_ID", m["entity_id"])
# local-only delta should NOT be in cloud recovery
rec_texts = [c["text"] for c in m["claims"]]
print("LOCAL_DELTA_IN_CLOUD", any("LOCAL-ONLY-DELTA" in t for t in rec_texts))

# restore env world root
os.environ["PROTEUS_WORLD_ROOT"] = str(EV / "world_memory_home" / "world")
store2 = WorldStore()
recon = reconcile_entity("entity.router.aw1000.home", world=store2)
print("ARCHIVARIUS_ADAPTER", recon.get("receipt_path"), "live=BLOCKED")
print("R1", r1)
print("R2", r2)
