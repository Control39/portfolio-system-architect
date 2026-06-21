#!/bin/bash
# agent_self_analyze_quick.sh - Быстрый самоанализ

cd /c/repo
source .venv/Scripts/activate

python scripts/agent_self_analyze_quick.py
