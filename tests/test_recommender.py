import pandas as pd

from src.recommender import HybridRecommender


def fixture_data():
    users = pd.DataFrame({"user_id": ["U1", "U2", "U3"]})
    catalog = pd.DataFrame({
        "item_id": ["T1", "T2", "T3", "T4"], "title": ["A", "B", "C", "D"],
        "type": ["Filme"] * 4, "genres": ["Ação", "Ação|Drama", "Comédia", "Drama"],
        "release_year": [2022, 2024, 2023, 2025], "quality_score": [8, 7, 9, 8],
    })
    interactions = pd.DataFrame({
        "user_id": ["U1", "U1", "U2", "U2", "U3", "U3"],
        "item_id": ["T1", "T2", "T1", "T3", "T2", "T4"],
        "event_weight": [4, 3, 3, 4, 4, 3],
    })
    return users, catalog, interactions


def test_recommendations_exclude_seen():
    users, catalog, interactions = fixture_data()
    model = HybridRecommender(factors=2).fit(users, catalog, interactions)
    result = model.recommend("U1", n=2)
    assert not set(result.item_id) & {"T1", "T2"}
    assert result["score"].notna().all()
    assert result["reason"].str.len().min() > 10


def test_cold_start_returns_requested_size():
    users, catalog, interactions = fixture_data()
    model = HybridRecommender(factors=2).fit(users, catalog, interactions)
    assert len(model.cold_start(["Drama"], n=3)) == 3

