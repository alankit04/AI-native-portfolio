#!/usr/bin/env bash
set -euo pipefail

python -m pip install --no-build-isolation -e .[dev]

echo "Installed editable dev package with --no-build-isolation"
