#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
npm install --ignore-scripts
npx prisma generate
