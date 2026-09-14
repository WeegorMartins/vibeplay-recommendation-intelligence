from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


GENRES = [
    "Ação", "Aventura", "Comédia", "Drama", "Documentário", "Ficção científica",
    "Romance", "Suspense", "Terror", "Animação", "Crime", "Família",
]
REGIONS = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
DEVICES = ["Smart TV", "Mobile", "Desktop", "Tablet"]
EVENTS = {"skip": -1.0, "play": 1.0, "complete": 3.0, "like": 4.0}


def _pick_genres(rng: np.random.Generator, primary: str) -> str:
    count = int(rng.choice([1, 2, 3], p=[0.42, 0.46, 0.12]))
    extras = rng.choice([g for g in GENRES if g != primary], size=count - 1, replace=False)
    return "|".join([primary, *extras.tolist()])


def generate(output_dir: Path, n_users: int = 800, n_items: int = 240, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    item_ids = [f"T{i:04d}" for i in range(1, n_items + 1)]
    primary_genre = rng.choice(GENRES, n_items)
    quality = np.clip(rng.normal(7.1, 1.0, n_items), 3.8, 9.7)
    years = rng.choice(np.arange(2000, 2027), n_items, p=np.linspace(0.5, 1.8, 27) / np.linspace(0.5, 1.8, 27).sum())
    title_type = rng.choice(["Filme", "Série"], n_items, p=[0.61, 0.39])
    catalog = pd.DataFrame({
        "item_id": item_ids,
        "title": [f"{g} em Cena {i:03d}" for i, g in enumerate(primary_genre, 1)],
        "type": title_type,
        "genres": [_pick_genres(rng, g) for g in primary_genre],
        "release_year": years,
        "duration_min": np.where(title_type == "Filme", rng.integers(78, 154, n_items), rng.integers(24, 62, n_items)),
        "quality_score": np.round(quality, 2),
        "maturity_rating": rng.choice(["Livre", "10", "12", "14", "16", "18"], n_items, p=[.11, .10, .23, .27, .22, .07]),
    })

    user_ids = [f"U{i:04d}" for i in range(1, n_users + 1)]
    # A moderately concentrated preference distribution creates realistic
    # taste clusters while preserving exploration and noise.
    prefs = rng.dirichlet(np.repeat(0.28, len(GENRES)), n_users)
    top_idx = np.argsort(-prefs, axis=1)[:, :3]
    users = pd.DataFrame({
        "user_id": user_ids,
        "region": rng.choice(REGIONS, n_users, p=[.46, .16, .24, .08, .06]),
        "age_group": rng.choice(AGE_GROUPS, n_users, p=[.18, .34, .25, .14, .09]),
        "plan": rng.choice(["Basic", "Standard", "Premium"], n_users, p=[.36, .40, .24]),
        "main_device": rng.choice(DEVICES, n_users, p=[.43, .36, .14, .07]),
        "favorite_genres": ["|".join(GENRES[j] for j in row) for row in top_idx],
        "tenure_months": rng.integers(1, 49, n_users),
    })

    genre_to_idx = {g: i for i, g in enumerate(GENRES)}
    item_affinity = np.zeros((n_items, len(GENRES)))
    for i, genre_str in enumerate(catalog["genres"]):
        for g in genre_str.split("|"):
            item_affinity[i, genre_to_idx[g]] = 1.0
        item_affinity[i] /= item_affinity[i].sum()

    rows: list[dict] = []
    end = pd.Timestamp("2026-09-13")
    global_pop = rng.pareto(2.2, n_items) + 0.25
    global_pop /= global_pop.max()
    for u, user_id in enumerate(user_ids):
        n_events = int(rng.integers(28, 66))
        scores = item_affinity @ prefs[u] * 5.0 + global_pop * 0.75 + quality / 10 * 0.45
        probabilities = np.exp(scores - scores.max())
        probabilities /= probabilities.sum()
        # One summarized outcome per user-title keeps offline discovery evaluation
        # from rewarding or penalizing repeat plays of an already-consumed item.
        chosen = rng.choice(n_items, n_events, replace=False, p=probabilities)
        for seq, item_idx in enumerate(chosen):
            affinity = float(item_affinity[item_idx] @ prefs[u])
            positive_p = np.clip(.38 + affinity * 2.8 + quality[item_idx] / 25, .42, .94)
            if rng.random() < positive_p:
                event = rng.choice(["play", "complete", "like"], p=[.35, .43, .22])
                pct = {"play": rng.uniform(.18, .72), "complete": rng.uniform(.82, 1), "like": rng.uniform(.72, 1)}[event]
            else:
                event, pct = "skip", rng.uniform(.01, .16)
            days_ago = int(np.clip(rng.exponential(52), 0, 179))
            rows.append({
                "interaction_id": f"I{len(rows)+1:07d}",
                "user_id": user_id,
                "item_id": item_ids[item_idx],
                "event_type": event,
                "event_weight": EVENTS[event],
                "watch_pct": round(float(pct), 4),
                "event_ts": (end - pd.Timedelta(days=days_ago, hours=int(rng.integers(0, 24)))).isoformat(),
                "session_id": f"S{u:04d}{seq//4:03d}",
                "source": rng.choice(["Home", "Busca", "Minha lista", "Top 10"], p=[.59, .19, .12, .10]),
            })
    interactions = pd.DataFrame(rows).sort_values("event_ts").reset_index(drop=True)

    catalog.to_csv(output_dir / "catalog.csv", index=False)
    users.to_csv(output_dir / "users.csv", index=False)
    interactions.to_csv(output_dir / "interactions.csv", index=False)
    print(f"Generated {len(users):,} users, {len(catalog):,} titles and {len(interactions):,} interactions in {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument("--users", type=int, default=800)
    parser.add_argument("--items", type=int, default=240)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(args.output, args.users, args.items, args.seed)
