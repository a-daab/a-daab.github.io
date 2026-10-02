#!/usr/bin/env python3
"""Switch search-engine indexing on (launch) or off (test build), then rebuild.
    python3 tools/set-indexing.py index     # launch: removes noindex and the test-build footer note
    python3 tools/set-indexing.py noindex"""
import json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode not in ("index", "noindex"): sys.exit(__doc__)
p = ROOT / "src/site.json"
s = json.loads(p.read_text(encoding="utf-8"))
s["noindex"] = s["test_build"] = (mode == "noindex")
p.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
subprocess.check_call([sys.executable, str(ROOT / "tools/build.py")])
