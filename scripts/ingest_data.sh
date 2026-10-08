#!/usr/bin/env bash
set -euo pipefail

# Pull latest changes
git pull --ff-only origin main

# Run the ingestion pipeline
sudo docker compose run --rm --build pipeline
