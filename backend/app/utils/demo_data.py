"""Loader for the synthetic demo disaster scenario used to seed the system."""
from __future__ import annotations

import json
from functools import lru_cache

from app.config import DEMO_DIR

SCENARIO_PATH = DEMO_DIR / "demo_scenario.json"


@lru_cache(maxsize=1)
def load_demo_scenario() -> dict:
    with open(SCENARIO_PATH, encoding="utf-8") as f:
        return json.load(f)
