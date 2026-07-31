#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
bash deploy/linux/stop.sh
bash deploy/linux/start.sh
