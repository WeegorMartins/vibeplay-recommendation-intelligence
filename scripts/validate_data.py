from pathlib import Path

import pandas as pd


ROOT = Path("data/raw")
users = pd.read_csv(ROOT / "users.csv")
catalog = pd.read_csv(ROOT / "catalog.csv")
events = pd.read_csv(ROOT / "interactions.csv", parse_dates=["event_ts"])

errors = []
for frame, keys, name in [(users, ["user_id"], "users"), (catalog, ["item_id"], "catalog"), (events, ["interaction_id", "user_id", "item_id", "event_ts"], "interactions")]:
    if frame[keys].isna().any().any():
        errors.append(f"{name}: nulls in required columns")
if users.user_id.duplicated().any(): errors.append("users: duplicate user_id")
if catalog.item_id.duplicated().any(): errors.append("catalog: duplicate item_id")
if events.interaction_id.duplicated().any(): errors.append("interactions: duplicate interaction_id")
if not set(events.user_id).issubset(set(users.user_id)): errors.append("interactions: orphan user_id")
if not set(events.item_id).issubset(set(catalog.item_id)): errors.append("interactions: orphan item_id")
if not events.watch_pct.between(0, 1).all(): errors.append("interactions: watch_pct outside [0, 1]")
if not set(events.event_type).issubset({"skip", "play", "complete", "like"}): errors.append("interactions: invalid event_type")
if events.event_ts.max() > pd.Timestamp("2026-09-14"): errors.append("interactions: future event")

if errors:
    raise SystemExit("Data contract failed:\n- " + "\n- ".join(errors))
print(f"Data contract passed: {len(users):,} users, {len(catalog):,} titles, {len(events):,} interactions.")

