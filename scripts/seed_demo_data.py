#!/usr/bin/env python3
"""
Seed demo data: initializes the SQLite database and prints a summary of the
synthetic demo scenario (Salem District flood) that ships with the project.

Usage:
    cd backend
    python ../scripts/seed_demo_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database.db import init_db
from app.utils.demo_data import load_demo_scenario


def main():
    init_db()
    scenario = load_demo_scenario()
    print("Demo data initialized.")
    print(f"Disaster: {scenario['disaster']['name']} ({scenario['disaster']['type']}, severity={scenario['disaster']['severity']})")
    print(f"Locations: {len(scenario['locations'])}")
    print(f"Shelters: {len(scenario['shelters'])}")
    print(f"Resources: {len(scenario['resources'])}")
    print(f"Agencies: {len(scenario['agencies'])}")
    print(f"Hospitals: {len(scenario['hospitals'])}")
    print(f"Incidents: {len(scenario['incidents'])}")
    print("\nNext steps:")
    print("  python scripts/build_graph.py")
    print("  python scripts/build_vector_index.py")


if __name__ == "__main__":
    main()
