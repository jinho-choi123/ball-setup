#!/bin/bash
set -euo pipefail
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uvx --from "git+https://github.com/jinho-choi123/ball-setup@feat/python-rewrite" ball-setup "$@"
