#!/usr/bin/env bash
# One-time setup on a Mac or Linux. Run:  bash setup-mac.sh
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null || ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "Install Python 3.10+ from https://www.python.org/downloads/ and run this again."; exit 1
fi
[ -x .venv/bin/python ] || python3 -m venv .venv
. .venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
python -m playwright install chromium
[ -f .env ] || { cp .env.example .env; echo "Created .env for your keys."; }
python council.py status
echo
echo "Next: put your API keys in business/tools/.env, then run:  source .venv/bin/activate"
echo "Daily:  python scout.py run   (then open business/data/outbox/<date>/today.html)"
