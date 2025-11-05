from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable, Tuple

from transformers import pipeline

from .config import settings


@lru_cache(maxsize=1)
def get_classifier():
    token = settings.huggingface_token or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if token:
        os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", token)
    return pipeline("zero-shot-classification", model=settings.huggingface_model)


def classify_area(product_name: str, descripcion: str, candidate_labels: Iterable[str]) -> Tuple[str, float]:
    classifier = get_classifier()
    text = f"Producto: {product_name}. Descripción: {descripcion}"
    result = classifier(
        text,
        candidate_labels=list(candidate_labels),
        hypothesis_template="Esta reclamación corresponde al área de {}.",
    )
    label = result["labels"][0]
    score = float(result["scores"][0])
    return label, score
