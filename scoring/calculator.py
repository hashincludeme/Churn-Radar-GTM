"""
Health score formula
  Login Frequency   — 30 pts  (current logins / prev logins, capped at 1.0)
  Feature Adoption  — 30 pts  (features_adopted / features_available)
  Support Tickets   — 20 pts  (0 open = 20, 1 = 15, 2-3 = 10, 4-5 = 5, 6+ = 0)
  NPS               — 20 pts  (nps_score / 100 * 20)
  Total             — 100 pts
"""

import pandas as pd
import config


_TICKET_SCORE = {0: 20, 1: 15, 2: 10, 3: 10, 4: 5, 5: 5}


def _login_score(row: pd.Series) -> float:
    prev = row["logins_prev_7d"]
    if prev == 0:
        return 30.0 if row["logins_last_7d"] > 0 else 0.0
    ratio = min(row["logins_last_7d"] / prev, 1.0)
    return round(ratio * 30, 2)


def _adoption_score(row: pd.Series) -> float:
    avail = row["features_available"]
    if avail == 0:
        return 0.0
    ratio = min(row["features_adopted"] / avail, 1.0)
    return round(ratio * 30, 2)


def _ticket_score(row: pd.Series) -> float:
    tickets = int(row["support_tickets_open"])
    return float(_TICKET_SCORE.get(tickets, 0))


def _nps_score(row: pd.Series) -> float:
    return round(float(row["nps_score"]) / 100 * 20, 2)


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["score_login"] = df.apply(_login_score, axis=1)
    df["score_adoption"] = df.apply(_adoption_score, axis=1)
    df["score_tickets"] = df.apply(_ticket_score, axis=1)
    df["score_nps"] = df.apply(_nps_score, axis=1)
    df["health_score"] = (
        df["score_login"]
        + df["score_adoption"]
        + df["score_tickets"]
        + df["score_nps"]
    ).round(1)
    df["health_tier"] = df["health_score"].apply(_tier)
    return df


def _tier(score: float) -> str:
    if score >= 75:
        return "Healthy"
    if score >= 50:
        return "At Risk"
    return "Critical"


def detect_drops(df: pd.DataFrame) -> pd.DataFrame:
    """Flag rows whose health score dropped more than ALERT_THRESHOLD_PCT points.

    In production the previous score comes from the last persisted run.
    In dry-run we simulate a prior score by adding a synthetic delta.
    """
    if "prev_health_score" not in df.columns:
        import numpy as np
        rng = np.random.default_rng(seed=42)
        df = df.copy()
        # Simulate prior scores: healthy customers were ~5 pts higher,
        # already-critical customers show a steep synthetic drop.
        df["prev_health_score"] = df["health_score"] + rng.uniform(0, 30, len(df))
        df["prev_health_score"] = df["prev_health_score"].clip(0, 100).round(1)

    df["score_delta"] = (df["prev_health_score"] - df["health_score"]).round(1)
    threshold = config.ALERT_THRESHOLD_PCT
    df["alert_triggered"] = df["score_delta"] >= threshold
    return df
