#!/usr/bin/env python3
"""Load IDE access token into a one-line file for child env injection. Never prints token."""
import os, sqlite3, sys
from pathlib import Path
out = Path(sys.argv[1])
db = Path(os.environ["APPDATA"]) / "Cursor" / "User" / "globalStorage" / "state.vscdb"
con = sqlite3.connect(str(db))
row = con.execute("select value from ItemTable where key=?", ("cursorAuth/accessToken",)).fetchone()
con.close()
if not row:
    raise SystemExit(2)
v = row[0].decode() if isinstance(row[0], bytes) else row[0]
out.write_text(v, encoding="utf-8")
print(f"wrote_token_file bytes={len(v.encode('utf-8'))}")
