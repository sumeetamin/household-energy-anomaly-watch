"""Benchmark a causal rolling robust alert on household power time series."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, precision_score, recall_score, roc_auc_score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--date", default="Date")
    parser.add_argument("--time", default="Time")
    parser.add_argument("--value", default="Global_active_power")
    parser.add_argument("--alert-budget", type=float, default=0.01)
    parser.add_argument("--out", default="outputs")
    args = parser.parse_args()

    source = Path(args.input)
    data = pd.read_csv(source, sep=";", na_values=["?"], low_memory=False)
    data["timestamp"] = pd.to_datetime(
        data[args.date].astype(str) + " " + data[args.time].astype(str),
        dayfirst=True,
        errors="coerce",
    )
    data[args.value] = pd.to_numeric(data[args.value], errors="coerce")
    series = (
        data.dropna(subset=["timestamp", args.value])
        .set_index("timestamp")[args.value]
        .sort_index()
        .resample("5min")
        .mean()
        .dropna()
    )
    if len(series) < 1000:
        raise SystemExit("At least 1,000 valid five-minute observations are required.")

    train_end = int(len(series) * 0.60)
    validation_end = int(len(series) * 0.70)
    train, validation, holdout = (
        series.iloc[:train_end],
        series.iloc[train_end:validation_end],
        series.iloc[validation_end:],
    )
    # The extreme-use proxy is defined using training values only.
    proxy_cutoff = float(train.quantile(0.99))
    proxy = (series > proxy_cutoff).astype(int)

    # Shift the rolling reference by one observation so the current reading
    # cannot influence its own baseline. Keep a fixed six-hour lookback.
    prior = series.shift(1)
    rolling_median = prior.rolling("6h", min_periods=24).median()
    rolling_mad = (prior - rolling_median).abs().rolling("6h", min_periods=24).median()
    robust_z = 0.6745 * (series - rolling_median) / rolling_mad.replace(0, np.nan)
    validation_score = robust_z.iloc[train_end:validation_end].replace([np.inf, -np.inf], np.nan).dropna()
    if validation_score.empty:
        raise SystemExit("Validation window has no scoreable observations.")
    # Choose a threshold on validation data to meet the declared review budget.
    threshold = float(validation_score.quantile(1 - args.alert_budget))
    score = robust_z.iloc[validation_end:].replace([np.inf, -np.inf], np.nan)
    valid = score.notna()
    score = score[valid]
    proxy = proxy.iloc[validation_end:][valid]
    alert = (score >= threshold).astype(int)
    y = proxy.to_numpy()
    prediction = alert.to_numpy()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "dataset": "UCI Individual Household Electric Power Consumption",
        "source_url": "https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption",
        "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "input_rows": int(len(data)),
        "resampled_points": int(len(series)),
        "train_points": int(len(train)),
        "validation_points": int(len(validation)),
        "holdout_points_scored": int(len(y)),
        "date_range": [series.index.min().isoformat(), series.index.max().isoformat()],
        "validation_start": validation.index.min().isoformat(),
        "holdout_start": holdout.index.min().isoformat(),
        "alert_budget": args.alert_budget,
        "selected_threshold": threshold,
        "proxy_definition": "Global active power above the training-period 99th percentile; this is an extreme-use proxy, not a labeled fault or safety incident.",
        "proxy_cutoff_kw": proxy_cutoff,
        "proxy_prevalence_holdout": float(np.mean(y)),
        "alert_rate_holdout": float(np.mean(prediction)),
        "alert_precision_vs_proxy": float(precision_score(y, prediction, zero_division=0)),
        "alert_recall_vs_proxy": float(recall_score(y, prediction, zero_division=0)),
        "average_precision_robust_z": float(average_precision_score(y, score.to_numpy())),
        "roc_auc_robust_z": float(roc_auc_score(y, score.to_numpy())) if len(np.unique(y)) == 2 else None,
        "method": "5-minute means; 60/10/30 chronological train/validation/holdout; one-sided causal six-hour rolling median/MAD; threshold selected on validation to meet the declared alert budget",
        "limitations": "Single household, one chronological holdout, and proxy labels derived from power magnitude. Alerts are review candidates only and do not indicate equipment failure or unsafe conditions.",
    }
    (out / "benchmark.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
