import json
import matplotlib.pyplot as plt
from pathlib import Path

FIELDS = [
    "product_line",
    "origin_port_code",
    "destination_port_code",
    "incoterm",
    "cargo_weight_kg",
    "cargo_cbm",
    "is_dangerous",
]

BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    with open(BASE_DIR / "output.json") as f:
        preds_list = json.load(f)
    preds = {r["id"]: r for r in preds_list}

    with open(BASE_DIR / "data" / "ground_truth.json") as f:
        gt_list = json.load(f)
    gt = {row["id"]: row for row in gt_list}

    accuracies = []

    for field in FIELDS:
        total = 0
        correct = 0
        for k, gt_row in gt.items():
            if k not in preds:
                continue
            total += 1
            if preds[k].get(field) == gt_row.get(field):
                correct += 1
        accuracies.append(correct / total if total else 0)

    plt.figure()
    plt.bar(FIELDS, accuracies)
    plt.ylim(0, 1)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Accuracy")
    plt.title("Per-field Extraction Accuracy")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
