from __future__ import annotations
"""
Validated model integration point.

This starter never fabricates probabilities. Until model artifacts are added,
predict_game() returns None.
"""
from .config import ROOT

MODEL_DIR = ROOT / "models"

def model_available() -> bool:
    return (MODEL_DIR / "model_metadata.json").exists()

def predict_game(*args, **kwargs):
    if not model_available():
        return None
    raise NotImplementedError(
        "Wire the validated NFL EDGE model artifact into predict_game()."
    )
