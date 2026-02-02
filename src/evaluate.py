import json
from typing import Dict, Any


FIELDS = [
    "product_line",
    "origin_port_code",
    "destination_port_code",
    "incoterm",
    "cargo_weight_kg",
    "cargo_cbm",
    "is_dangerous",
]


def normalize_value(v):
    """
    Normalize values for fair comparison.
    """
    if v is None:
        return None

    if isinstance(v, str):
        return v.strip().upper()

    if isinstance(v, float):
        return round(v, 2)

    return v


def values_equal(pred, gt) -> bool:
    """
    Exact match after normalization.
    """
    return normalize_value(pred) == normalize_value(gt)


def evaluate(predictions: Dict[str, Any], ground_truth: Dict[str, Any]):
    total = 0
    correct = 0

    per_field_correct = {f: 0 for f in FIELDS}
    per_field_total = {f: 0 for f in FIELDS}

    for email_id, gt_row in ground_truth.items():
        pred_row = predictions.get(email_id)
        if pred_row is None:
            continue

        for field in FIELDS:
            gt_val = gt_row.get(field)
            pred_val = pred_row.get(field)

            per_field_total[field] += 1
            total += 1

            if values_equal(pred_val, gt_val):
                correct += 1
                per_field_correct[field] += 1
            else:
                print(pred_row)

    accuracy = correct / total if total else 0.0

    print("\n=== OVERALL ACCURACY ===")
    print(f"{accuracy:.2%}")

    print("\n=== FIELD BREAKDOWN ===")
    for field in FIELDS:
        if per_field_total[field] == 0:
            continue
        acc = per_field_correct[field] / per_field_total[field]
        print(f"{field:25s}: {acc:.2%}")

    return accuracy


def main():
    with open("../output.json", "r") as f:
        preds_list = json.load(f)

    with open("../data/ground_truth.json", "r") as f:
        gt_list = json.load(f)

    predictions = {row["id"]: row for row in preds_list}
    ground_truth = {row["id"]: row for row in gt_list}

    evaluate(predictions, ground_truth)


if __name__ == "__main__":
    main()
