#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install -e .
python3 /Users/jeesubkim/Project/sms/scripts/run_tests.py
