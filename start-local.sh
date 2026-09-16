#!/usr/bin/env bash

# Starts the API and Vite development server together for local development.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PID=""

cleanup() {
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill "${BACKEND_PID}"
  fi
}

trap cleanup EXIT INT TERM

(
  cd "${ROOT_DIR}/backend"
  exec python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &
BACKEND_PID=$!

cd "${ROOT_DIR}/frontend"
npm run dev
