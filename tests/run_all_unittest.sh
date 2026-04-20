#!/usr/bin/env bash
set -euo pipefail

# Simple runner for environments without pytest installed.
# Discovers and runs unittest-based tests under tests/.

echo "Running unittest suite..."
python -m unittest discover -s tests -p "test_*.py" -t .
echo " unittest run complete."
