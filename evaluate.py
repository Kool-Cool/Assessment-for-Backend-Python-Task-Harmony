import json
import os
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    f1_score
)
import matplotlib.pyplot as plt
import seaborn as sns



# CONFIG

FIELDS_CLASS = [
    "product_line",
    "incoterm",
    "origin_port_code",
    "destination_port_code",
    "is_dangerous"
]

FIELDS_NUM = [
    "cargo_weight_kg",
    "cargo_cbm"
]



# SAFE COMPARE

def safe_equal(gt_val, pred_val):
    if pd.isna(gt_val) and pd.isna(pred_val):
        return True
    if pd.isna(gt_val) or pd.isna(pred_val):
        return False

    # numeric check
    try:
        return float(gt_val) == float(pred_val)
    except:
        return str(gt_val).strip().lower() == str(pred_val).strip().lower()


# LOAD DATA

def load_data(gt_file, pred_file):
    gt = {x["id"]: x for x in json.load(open(gt_file))}
    pred = {x["id"]: x for x in json.load(open(pred_file))}
    return gt, pred



# MAIN EVAL

def evaluate(pred_file, gt_file):

    run_name = pred_file.split("/")[-1].replace(".json", "")
    out_dir = f"evaluation/{run_name}"
    os.makedirs(out_dir, exist_ok=True)

    gt, pred = load_data(gt_file, pred_file)

    rows = []

    for id in gt:
        if id not in pred:
            continue

        row = {"id": id}

        for f in FIELDS_CLASS:
            row[f + "_gt"] = gt[id].get(f)
            row[f + "_pred"] = pred[id].get(f)

        for f in FIELDS_NUM:
            row[f + "_gt"] = gt[id].get(f)
            row[f + "_pred"] = pred[id].get(f)

        rows.append(row)

    df = pd.DataFrame(rows)

    metrics = {}

    
    # CLASSIFICATION METRICS
    
    print("\n=== CLASSIFICATION METRICS ===")

    for f in FIELDS_CLASS:
        mask = df[f + "_gt"].notna() & df[f + "_pred"].notna()
        y_true = df.loc[mask, f + "_gt"]
        y_pred = df.loc[mask, f + "_pred"]

        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred, average="weighted")

        metrics[f] = {
            "accuracy": float(acc),
            "f1": float(f1)
        }

        print(f"{f}: acc={acc:.3f} f1={f1:.3f}")

        # confusion matrix
        # labels = sorted(list(set(y_true.dropna().tolist() + y_pred.dropna().tolist())))
        labels = sorted(set(map(str, y_true)) | set(map(str, y_pred)))        
        cm = confusion_matrix(y_true, y_pred, labels=labels)

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels)
        plt.title(f"Confusion Matrix - {f}")
        plt.tight_layout()
        plt.savefig(f"{out_dir}/{f}_confusion_matrix.png")
        plt.close()

    
    # NUMERIC METRICS
    
    print("\n=== NUMERIC METRICS ===")

    for f in FIELDS_NUM:
        mask = df[f + "_gt"].notna() & df[f + "_pred"].notna()

        y_true = df.loc[mask, f + "_gt"].astype(float)
        y_pred = df.loc[mask, f + "_pred"].astype(float)

        mae = mean_absolute_error(y_true, y_pred)

        # % within tolerance
        denom = np.where(y_true == 0, 1, y_true)
        # tol = np.abs(y_true - y_pred) / (y_true + 1e-6)
        tol = np.abs(y_true - y_pred) / denom
        within_5 = (tol < 0.05).mean()
        within_10 = (tol < 0.10).mean()

        metrics[f] = {
            "mae": float(mae),
            "within_5%": float(within_5),
            "within_10%": float(within_10)
        }

        print(f"{f}: MAE={mae:.2f}, 5%={within_5:.2f}, 10%={within_10:.2f}")

        # error distribution plot
        plt.figure()
        (y_pred - y_true).hist(bins=20)
        plt.title(f"Error Distribution - {f}")
        plt.savefig(f"{out_dir}/{f}_error_dist.png")
        plt.close()

    
    # FULL RECORD ACCURACY
    
    full_correct = 0

    for _, r in df.iterrows():
        ok = True

        for f in FIELDS_CLASS :
            if not safe_equal(r[f + "_gt"], r[f + "_pred"]):
                ok = False
                break


        # numeric fields (strict numeric compare)
        if ok:
            for f in FIELDS_NUM:
                gt_val = r[f + "_gt"]
                pred_val = r[f + "_pred"]

                if pd.isna(gt_val) and pd.isna(pred_val):
                    continue

                if pd.isna(gt_val) or pd.isna(pred_val):
                    ok = False
                    break

                if abs(float(gt_val) - float(pred_val)) > 1e-6:
                    ok = False
                    break


        if ok:
            full_correct += 1

    full_acc = full_correct / len(df)

    metrics["full_record_accuracy"] = full_acc

    print("\nFULL RECORD ACCURACY:", full_acc)

    
    # SAVE METRICS
    
    with open(f"{out_dir}/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    df.to_csv(f"{out_dir}/pred_vs_gt.csv", index=False)

    print(f"\nSaved evaluation to: {out_dir}")


if __name__ == "__main__":
    evaluate(
        pred_file="./extract/output_20260322_110616.json",
        gt_file="./ground_truth.json"
    )