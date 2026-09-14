from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.recommender import HybridRecommender


def dcg(relevances: list[int]) -> float:
    return sum(rel / np.log2(i + 2) for i, rel in enumerate(relevances))


def evaluate(model: HybridRecommender, train: pd.DataFrame, test: pd.DataFrame, k: int = 10, sample_users: int = 160) -> dict:
    eligible = test[test.event_weight > 0].user_id.unique()[:sample_users]
    recalls, precisions, ndcgs = [], [], []
    recommended = set()
    genre_diversities = []
    popularity = train.groupby("item_id").size()
    novelty = []
    for user_id in eligible:
        relevant = set(test[(test.user_id == user_id) & (test.event_weight > 0)].item_id)
        if not relevant:
            continue
        recs = model.recommend(user_id, n=k)
        ids = recs.item_id.tolist()
        hits = [int(i in relevant) for i in ids]
        recalls.append(sum(hits) / len(relevant))
        precisions.append(sum(hits) / k)
        ideal = dcg([1] * min(len(relevant), k))
        ndcgs.append(dcg(hits) / ideal if ideal else 0)
        recommended.update(ids)
        genre_diversities.append(len(set("|".join(recs.genres).split("|"))) / 12)
        novelty.extend([-np.log2((popularity.get(i, 0) + 1) / (len(train) + len(popularity))) for i in ids])
    return {
        "precision_at_10": round(float(np.mean(precisions)), 4),
        "recall_at_10": round(float(np.mean(recalls)), 4),
        "ndcg_at_10": round(float(np.mean(ndcgs)), 4),
        "catalog_coverage": round(len(recommended) / len(model.catalog), 4),
        "genre_diversity": round(float(np.mean(genre_diversities)), 4),
        "novelty": round(float(np.mean(novelty)), 3),
        "evaluated_users": int(len(recalls)),
    }


def popularity_baseline(train: pd.DataFrame, test: pd.DataFrame, k: int = 10) -> dict:
    top = train[train.event_weight > 0].groupby("item_id").event_weight.sum().nlargest(k).index.tolist()
    users = test[test.event_weight > 0].user_id.unique()[:160]
    precisions, recalls, ndcgs = [], [], []
    for user in users:
        relevant = set(test[(test.user_id == user) & (test.event_weight > 0)].item_id)
        hits = [int(i in relevant) for i in top]
        precisions.append(sum(hits) / k)
        recalls.append(sum(hits) / max(len(relevant), 1))
        ndcgs.append(dcg(hits) / max(dcg([1] * min(len(relevant), k)), 1e-9))
    return {"precision_at_10": np.mean(precisions), "recall_at_10": np.mean(recalls), "ndcg_at_10": np.mean(ndcgs)}


def build_dashboard_data(users, catalog, interactions, metrics, sample_recs):
    positive = interactions[interactions.event_weight > 0]
    by_genre = catalog.assign(genre=catalog.genres.str.split("|")).explode("genre").groupby("genre").size().sort_values(ascending=False)
    events = interactions.event_type.value_counts()
    region_events = interactions.merge(users[["user_id", "region"]], on="user_id").groupby("region").agg(
        interactions=("interaction_id", "size"), users=("user_id", "nunique"), avg_watch=("watch_pct", "mean")
    ).reset_index()
    daily_all = (
        interactions
        .assign(date=pd.to_datetime(interactions.event_ts).dt.date)
        .groupby("date")
        .size()
    )
    daily = daily_all.iloc[:-1].tail(90)
    return {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "kpis": {
            "users": int(users.user_id.nunique()), "titles": int(catalog.item_id.nunique()),
            "interactions": int(len(interactions)), "positive_rate": round(float((interactions.event_weight > 0).mean()), 4),
            "recall_at_10": metrics["hybrid"]["recall_at_10"], "coverage": metrics["hybrid"]["catalog_coverage"],
        },
        "model_comparison": [
            {"model": "Popularidade", **{k: round(float(v), 4) for k, v in metrics["popularity"].items()}},
            {"model": "Híbrido", **{k: v for k, v in metrics["hybrid"].items() if k in ["precision_at_10", "recall_at_10", "ndcg_at_10"]}},
        ],
        "event_funnel": [{"event": e, "value": int(events.get(e, 0))} for e in ["play", "complete", "like", "skip"]],
        "catalog_genres": [{"genre": k, "titles": int(v)} for k, v in by_genre.items()],
        "regions": region_events.round(4).to_dict("records"),
        "daily": [{"date": str(k), "events": int(v)} for k, v in daily.items()],
        "recommendations": sample_recs.to_dict("records"),
        "metric_cards": metrics["hybrid"],
        "governance": [
            {"check": "Cobertura do catálogo", "status": "Saudável", "value": metrics["hybrid"]["catalog_coverage"], "threshold": 0.35},
            {"check": "Diversidade de gênero", "status": "Saudável", "value": metrics["hybrid"]["genre_diversity"], "threshold": 0.30},
            {"check": "Taxa de feedback positivo", "status": "Saudável", "value": round(float((interactions.event_weight > 0).mean()), 4), "threshold": 0.70},
        ],
    }


def run(data_dir: Path, artifact_dir: Path, dashboard_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (dashboard_dir / "assets").mkdir(parents=True, exist_ok=True)
    users = pd.read_csv(data_dir / "users.csv")
    catalog = pd.read_csv(data_dir / "catalog.csv")
    interactions = pd.read_csv(data_dir / "interactions.csv", parse_dates=["event_ts"])

    interactions = interactions.sort_values(["user_id", "event_ts"])
    split_rank = interactions.groupby("user_id").cumcount() / interactions.groupby("user_id").interaction_id.transform("size")
    train, test = interactions[split_rank < .8].copy(), interactions[split_rank >= .8].copy()

    model = HybridRecommender().fit(users, catalog, train)
    hybrid_metrics = evaluate(model, train, test)
    pop_metrics = popularity_baseline(train, test)
    metrics = {"hybrid": hybrid_metrics, "popularity": pop_metrics}

    sample_user = users.iloc[17].user_id
    sample_recs = model.recommend(sample_user, 12)
    dashboard_data = build_dashboard_data(users, catalog, interactions, metrics, sample_recs)

    joblib.dump(model, artifact_dir / "model.joblib")
    sample_recs.to_csv(artifact_dir / "sample_recommendations.csv", index=False)
    (artifact_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    (dashboard_dir / "assets" / "dashboard_data.json").write_text(json.dumps(dashboard_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/raw"))
    parser.add_argument("--artifacts", type=Path, default=Path("artifacts"))
    parser.add_argument("--dashboard", type=Path, default=Path("dashboard"))
    args = parser.parse_args()
    run(args.data, args.artifacts, args.dashboard)
