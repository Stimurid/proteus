from pathlib import Path
import re
import subprocess
import sys

r = subprocess.run(
    [sys.executable, "-m", "pytest", "tests", "-q", "--tb=line"],
    cwd=r"C:\projects\Proteus",
    capture_output=True,
    text=True,
)
print(r.stdout[-2000:] if r.stdout else "")
print(r.stderr[-500:] if r.stderr else "")
print("PYTEST_CODE", r.returncode)

ev = Path(r"C:\projects\Proteus\evidence\runs\PROTEUS-CURSOR-RUN-001-20260909T201711Z")
paths = list((ev / "world_memory_home/world/entities/entity.router.aw1000.home").rglob("*"))
paths += [
    ev / "drive_carrier_entity.router.aw1000.home.zip",
    ev / "AW1000_PROJECT_R1_STDOUT.txt",
    ev / "AW1000_PROJECT_R2_STDOUT.txt",
]
bad = []
for p in paths:
    if not p.is_file():
        continue
    data = p.read_bytes()
    if b"BEGIN RSA PRIVATE KEY" in data or b"BEGIN OPENSSH" in data:
        bad.append(("key", str(p)))
    text = data.decode("utf-8", "replace")
    if re.search(r'"plaintext"\s*:\s*"[^"]+"', text):
        bad.append(("plaintext", str(p)))
    if "SYNTHETIC-AW1000-BROKER-ONLY" in text:
        bad.append(("synth_in_entity", str(p)))
print("PLAINTEXT_SCAN", bad or "CLEAN")
