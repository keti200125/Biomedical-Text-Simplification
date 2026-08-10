"""Shared evaluation utilities for biomedical text simplification experiments.

This module centralizes SARI, BLEU, and BERTScore computation so notebooks
evaluate Llama, FLAN-T5, BioBART, KG-BioBART, action pipelines, and oracle
pipelines consistently.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import sacrebleu
from bert_score import score as bert_score

try:
    import evaluate
except ImportError: 
    evaluate = None


REQUIRED_PREDICTION_COLUMNS = ["complex", "simple", "prediction"]


def get_ngrams(tokens: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
    """Return n-gram counts for a token sequence."""
    if n <= 0:
        raise ValueError("n must be a positive integer")
    return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def safe_f1(precision: float, recall: float) -> float:
    """Compute F1 and return 0 when precision and recall are both 0."""
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def sari_sentence(source: str, prediction: str, reference: str, max_ngram: int = 4) -> float:
    """Compute a local sentence-level SARI approximation on a 0-100 scale."""
    source_tokens = str(source).lower().split()
    pred_tokens = str(prediction).lower().split()
    ref_tokens = str(reference).lower().split()

    add_scores: list[float] = []
    keep_scores: list[float] = []
    delete_scores: list[float] = []

    for n in range(1, max_ngram + 1):
        source_ngrams = set(get_ngrams(source_tokens, n))
        pred_ngrams = set(get_ngrams(pred_tokens, n))
        ref_ngrams = set(get_ngrams(ref_tokens, n))

        add_pred = pred_ngrams - source_ngrams
        add_ref = ref_ngrams - source_ngrams
        add_precision = len(add_pred & add_ref) / len(add_pred) if add_pred else 0.0
        add_recall = len(add_pred & add_ref) / len(add_ref) if add_ref else 0.0
        add_scores.append(safe_f1(add_precision, add_recall))

        keep_pred = pred_ngrams & source_ngrams
        keep_ref = ref_ngrams & source_ngrams
        keep_precision = len(keep_pred & keep_ref) / len(keep_pred) if keep_pred else 0.0
        keep_recall = len(keep_pred & keep_ref) / len(keep_ref) if keep_ref else 0.0
        keep_scores.append(safe_f1(keep_precision, keep_recall))

        delete_pred = source_ngrams - pred_ngrams
        delete_ref = source_ngrams - ref_ngrams
        delete_precision = len(delete_pred & delete_ref) / len(delete_pred) if delete_pred else 0.0
        delete_scores.append(delete_precision)

    return 100 * float(np.mean([np.mean(add_scores), np.mean(keep_scores), np.mean(delete_scores)]))


def _to_string_list(values: Iterable[object]) -> list[str]:
    """Convert iterable values to strings, replacing missing values with empty strings."""
    return pd.Series(list(values), dtype="object").fillna("").astype(str).tolist()


def compute_sari_score(
    sources: Sequence[object],
    predictions: Sequence[object],
    references: Sequence[object],
) -> float:
    """Compute corpus SARI on a 0-100 scale, falling back to local SARI if needed."""
    source_list = _to_string_list(sources)
    prediction_list = _to_string_list(predictions)
    reference_list = _to_string_list(references)

    if not (len(source_list) == len(prediction_list) == len(reference_list)):
        raise ValueError("sources, predictions, and references must have the same length")
    if len(source_list) == 0:
        return float("nan")

    if evaluate is not None:
        for metric_name in ["sari", "evaluate-metric/sari"]:
            try:
                sari_metric = evaluate.load(metric_name)
                result = sari_metric.compute(
                    sources=source_list,
                    predictions=prediction_list,
                    references=[[reference] for reference in reference_list],
                )
                return float(result["sari"])
            except Exception:
                continue

    scores = [
        sari_sentence(source, prediction, reference)
        for source, prediction, reference in zip(source_list, prediction_list, reference_list, strict=True)
    ]
    return float(np.mean(scores))


def compute_bleu_score(predictions: Sequence[object], references: Sequence[object]) -> float:
    """Compute corpus BLEU on a 0-100 scale."""
    prediction_list = _to_string_list(predictions)
    reference_list = _to_string_list(references)

    if len(prediction_list) != len(reference_list):
        raise ValueError("predictions and references must have the same length")
    if len(prediction_list) == 0:
        return float("nan")

    if evaluate is not None:
        try:
            bleu_metric = evaluate.load("bleu")
            result = bleu_metric.compute(predictions=prediction_list, references=[[ref] for ref in reference_list])
            bleu = float(result["bleu"])
            return bleu * 100 if bleu <= 1.0 else bleu
        except Exception:
            pass

    return float(sacrebleu.corpus_bleu(prediction_list, [reference_list]).score)


def compute_bertscore(predictions: Sequence[object], references: Sequence[object]) -> dict[str, float]:
    """Compute BERTScore precision, recall, and F1, skipping empty predictions."""
    prediction_list = _to_string_list(predictions)
    reference_list = _to_string_list(references)

    if len(prediction_list) != len(reference_list):
        raise ValueError("predictions and references must have the same length")

    filtered_pairs = [
        (prediction, reference)
        for prediction, reference in zip(prediction_list, reference_list, strict=True)
        if prediction.strip()
    ]
    if not filtered_pairs:
        return {
            "BERTScore Precision": float("nan"),
            "BERTScore Recall": float("nan"),
            "BERTScore F1": float("nan"),
        }

    filtered_predictions, filtered_references = zip(*filtered_pairs, strict=True)
    precision, recall, f1 = bert_score(
        list(filtered_predictions),
        list(filtered_references),
        lang="en",
        verbose=False,
    )
    return {
        "BERTScore Precision": float(precision.mean()),
        "BERTScore Recall": float(recall.mean()),
        "BERTScore F1": float(f1.mean()),
    }


def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute SARI, BLEU, and BERTScore for a prediction DataFrame."""
    missing_columns = [column for column in REQUIRED_PREDICTION_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Prediction DataFrame is missing required columns: {missing_columns}")

    metric_df = df[REQUIRED_PREDICTION_COLUMNS].copy()
    for column in REQUIRED_PREDICTION_COLUMNS:
        metric_df[column] = metric_df[column].fillna("").astype(str)

    sources = metric_df["complex"].tolist()
    references = metric_df["simple"].tolist()
    predictions = metric_df["prediction"].tolist()

    sari = compute_sari_score(sources, predictions, references)
    bleu = compute_bleu_score(predictions, references)
    bert = compute_bertscore(predictions, references)

    return pd.DataFrame(
        [
            {"metric": "SARI", "score": sari},
            {"metric": "BLEU", "score": bleu},
            {"metric": "BERTScore Precision", "score": bert["BERTScore Precision"]},
            {"metric": "BERTScore Recall", "score": bert["BERTScore Recall"]},
            {"metric": "BERTScore F1", "score": bert["BERTScore F1"]},
        ]
    )


def load_predictions(path: str | Path) -> pd.DataFrame:
    """Load a prediction CSV and validate required evaluation columns."""
    prediction_path = Path(path)
    df = pd.read_csv(prediction_path)
    missing_columns = [column for column in REQUIRED_PREDICTION_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(f"{prediction_path} is missing required columns: {missing_columns}")
    return df


def save_metrics(metrics_df: pd.DataFrame, path: str | Path) -> None:
    """Save metrics to CSV, creating parent directories when needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(output_path, index=False)

