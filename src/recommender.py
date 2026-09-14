from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


@dataclass(frozen=True)
class Weights:
    collaborative: float = 0.52
    content: float = 0.28
    popularity: float = 0.12
    freshness: float = 0.08


class HybridRecommender:
    """Hybrid implicit-feedback recommender with diversity re-ranking and explanations."""

    def __init__(self, weights: Weights = Weights(), factors: int = 24, diversity_lambda: float = 0.78):
        self.weights = weights
        self.factors = factors
        self.diversity_lambda = diversity_lambda

    def fit(self, users: pd.DataFrame, catalog: pd.DataFrame, interactions: pd.DataFrame):
        self.users = users.copy()
        self.catalog = catalog.copy().reset_index(drop=True)
        self.interactions = interactions.copy()
        self.user_ids = users["user_id"].tolist()
        self.item_ids = self.catalog["item_id"].tolist()
        self.user_to_idx = {v: i for i, v in enumerate(self.user_ids)}
        self.item_to_idx = {v: i for i, v in enumerate(self.item_ids)}

        agg = interactions.groupby(["user_id", "item_id"], as_index=False)["event_weight"].sum()
        agg = agg[agg.user_id.isin(self.user_to_idx) & agg.item_id.isin(self.item_to_idx)]
        rows = agg.user_id.map(self.user_to_idx).to_numpy()
        cols = agg.item_id.map(self.item_to_idx).to_numpy()
        values = np.maximum(agg.event_weight.to_numpy(), 0.05)
        self.matrix = csr_matrix((values, (rows, cols)), shape=(len(self.user_ids), len(self.item_ids)))

        n_components = min(self.factors, min(self.matrix.shape) - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.user_latent = normalize(self.svd.fit_transform(self.matrix))
        self.item_latent = normalize(self.svd.components_.T)

        text = self.catalog["genres"].str.replace("|", " ", regex=False) + " " + self.catalog["type"]
        self.vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b[\wÀ-ÿ-]+\b")
        self.item_content = normalize(self.vectorizer.fit_transform(text))

        pos = interactions.assign(pos=lambda x: x.event_weight.clip(lower=0)).groupby("item_id")["pos"].sum()
        self.popularity = np.log1p(self.catalog.item_id.map(pos).fillna(0).to_numpy())
        self.popularity /= max(self.popularity.max(), 1)
        newest = self.catalog.release_year.to_numpy() - self.catalog.release_year.min()
        self.freshness = newest / max(newest.max(), 1)
        return self

    def _profile(self, user_id: str):
        if user_id not in self.user_to_idx:
            raise KeyError(f"Unknown user: {user_id}")
        u = self.user_to_idx[user_id]
        history = self.matrix.getrow(u)
        if history.nnz:
            content_profile = normalize(history @ self.item_content).toarray().ravel()
            content_score = np.asarray(self.item_content @ content_profile).ravel()
        else:
            content_score = np.zeros(len(self.item_ids))
        collab_score = self.item_latent @ self.user_latent[u]
        collab_score = (collab_score - collab_score.min()) / max(np.ptp(collab_score), 1e-9)
        return u, history, collab_score, content_score

    def _explain(self, user_id: str, item_idx: int) -> str:
        item_genres = set(self.catalog.iloc[item_idx].genres.split("|"))
        hist = self.interactions[(self.interactions.user_id == user_id) & (self.interactions.event_weight >= 3)]
        liked = self.catalog[self.catalog.item_id.isin(hist.item_id)]
        overlap: list[str] = []
        for value in liked.genres:
            overlap.extend(set(value.split("|")) & item_genres)
        if overlap:
            genre = pd.Series(overlap).value_counts().index[0]
            return f"Porque você concluiu ou curtiu títulos de {genre}."
        if self.catalog.iloc[item_idx].release_year >= 2024:
            return "Uma novidade alinhada ao seu perfil, com boa avaliação."
        return "Popular entre pessoas com um padrão de consumo semelhante ao seu."

    def recommend(self, user_id: str, n: int = 10, exclude_seen: bool = True, apply_diversity: bool = True) -> pd.DataFrame:
        _, history, collab, content = self._profile(user_id)
        base = (
            self.weights.collaborative * collab
            + self.weights.content * content
            + self.weights.popularity * self.popularity
            + self.weights.freshness * self.freshness
        )
        if exclude_seen:
            base[history.indices] = -np.inf
        candidates = np.argsort(-base)[: max(n * 5, n)]
        selected: list[int] = []
        while len(selected) < n and len(selected) < len(candidates):
            if not selected or not apply_diversity:
                choice = next(i for i in candidates if i not in selected)
            else:
                pool = [i for i in candidates if i not in selected]
                mmr = []
                for i in pool:
                    similarity = max(float(self.item_content[i].multiply(self.item_content[j]).sum()) for j in selected)
                    mmr.append(self.diversity_lambda * base[i] - (1 - self.diversity_lambda) * similarity)
                choice = pool[int(np.argmax(mmr))]
            selected.append(choice)

        out = self.catalog.iloc[selected].copy()
        out["score"] = [round(float(base[i]), 4) for i in selected]
        out["reason"] = [self._explain(user_id, i) for i in selected]
        out.insert(0, "rank", np.arange(1, len(out) + 1))
        return out

    def cold_start(self, favorite_genres: Iterable[str], n: int = 10) -> pd.DataFrame:
        query = " ".join(favorite_genres)
        vector = self.vectorizer.transform([query])
        content = (self.item_content @ vector.T).toarray().ravel()
        score = .68 * content + .22 * self.popularity + .10 * self.freshness
        idx = np.argsort(-score)[:n]
        out = self.catalog.iloc[idx].copy()
        out["score"] = np.round(score[idx], 4)
        out["reason"] = f"Escolhido a partir dos interesses iniciais: {query}."
        out.insert(0, "rank", np.arange(1, len(out) + 1))
        return out
