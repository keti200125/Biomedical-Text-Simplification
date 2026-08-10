"""Preprocess sentence-level simplification data without document context.

This script prepares the Cochrane-auto sentence-level dataset for the first
PyTorch NLP experiment: direct sentence-to-sentence simplification.

It keeps only labels that have a sentence-level target text:
rephrase, ignore and split.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd


CODE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODE_DIR.parent
DATA_DIR = CODE_DIR / "data" if (CODE_DIR / "data").exists() else PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "sentence" / "raw"
OUTPUT_DIR = DATA_DIR / "processed" / "sentence_no_context"

SPLIT_FILES = {
    "train": "cochraneauto_sents_train.csv",
    "val": "cochraneauto_sents_val.csv",
    "test": "cochraneauto_sents_test.csv",
}

KEEP_LABELS = {"rephrase", "ignore", "split"}
OUTPUT_COLUMNS = ["pair_id", "sent_id", "label", "input_text", "target_text"]


def load_split(split_name: str, filename: str) -> pd.DataFrame:
    """Load one raw CSV split."""
    path = RAW_DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing {split_name} split: {path}")

    return pd.read_csv(path)


def parse_simple(value: object) -> str:
    """Parse the simple column from a string representation of a Python list.

    Examples:
    "['A simplified sentence.']" -> "A simplified sentence."
    "['First sentence.', 'Second sentence.']" -> "First sentence. Second sentence."
    "[]" -> ""
    """
    if isinstance(value, list):
        return " ".join(str(item).strip() for item in value if str(item).strip())

    if pd.isna(value):
        return ""

    text = str(value).strip()
    if not text:
        return ""

    try:
        parsed = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return text

    if isinstance(parsed, list):
        return " ".join(str(item).strip() for item in parsed if str(item).strip())

    if parsed is None:
        return ""

    return str(parsed).strip()


def preprocess_split(df: pd.DataFrame) -> pd.DataFrame:
    """Filter and convert one split into input/target text pairs."""
    required_columns = {"pair_id", "sent_id", "complex", "label", "simple"}
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    processed = df[df["label"].isin(KEEP_LABELS)].copy()
    processed["input_text"] = processed["complex"].fillna("").astype(str).str.strip()
    processed["target_text"] = processed["simple"].apply(parse_simple).str.strip()

    processed = processed[processed["target_text"].ne("")].copy()

    return processed[OUTPUT_COLUMNS].reset_index(drop=True)


def print_split_summary(
    split_name: str,
    original_df: pd.DataFrame,
    processed_df: pd.DataFrame,
) -> None:
    """Print dataset size and label distribution for one split."""
    print(f"\n=== {split_name} ===")
    print(f"Original dataset size: {len(original_df):,}")
    print(f"Filtered dataset size: {len(processed_df):,}")
    print("Label distribution:")

    if processed_df.empty:
        print("(empty split)")
        return

    label_distribution = (
        processed_df["label"]
        .value_counts()
        .rename_axis("label")
        .reset_index(name="count")
    )
    label_distribution["percentage"] = (
        label_distribution["count"] / len(processed_df) * 100
    )
    print(
        label_distribution.to_string(
            index=False,
            formatters={"percentage": "{:.2f}%".format},
        )
    )


def save_split(split_name: str, processed_df: pd.DataFrame) -> Path:
    """Save one processed split as CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{split_name}.csv"
    processed_df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    """Run preprocessing for train, validation and test splits."""
    print("Preprocessing sentence-level data without document context")
    print(f"Keeping labels: {sorted(KEEP_LABELS)}")
    print("Removing labels: delete, merge, none")

    for split_name, filename in SPLIT_FILES.items():
        original_df = load_split(split_name, filename)
        processed_df = preprocess_split(original_df)
        output_path = save_split(split_name, processed_df)

        print_split_summary(split_name, original_df, processed_df)
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
