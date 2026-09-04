#!/usr/bin/env bash
# Regenerates every shippable artefact, then refuses to finish if the
# workbooks do not pass verification.
set -euo pipefail
cd "$(dirname "$0")"

echo "== workbooks =="
python3 build.py
echo
echo "== buyer guide =="
python3 guide.py
echo
echo "== verification (LibreOffice recalculates, then we assert) =="
python3 verify.py
echo
echo "== listing copy limits =="
python3 check_listing.py | tail -3
echo
echo "== listing images =="
python3 mockups.py
echo
echo "all artefacts rebuilt and verified"
