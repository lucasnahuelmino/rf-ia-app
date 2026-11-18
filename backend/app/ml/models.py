from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression


class SignalClassifier:
    def __init__(self) -> None:
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self._trained = False

    def train(self, X: List[List[float]], y: List[Any]) -> None:
        self.model.fit(X, y)
        self._trained = True

    def predict(self, X: List[List[float]]) -> List[Any]:
        if not self._trained:
            raise RuntimeError("Model not trained")
        return self.model.predict(X).tolist()


class AnomalyDetector:
    def __init__(self) -> None:
        self.model = IsolationForest(random_state=42)

    def fit(self, X: List[List[float]]) -> None:
        self.model.fit(X)

    def predict(self, X: List[List[float]]) -> List[int]:
        return self.model.predict(X).tolist()