# Household Energy Anomaly Watch

A reproducible single-home energy monitoring prototype. It scores unusually high five-minute average power readings against a causal, rolling robust baseline and exports aggregate evaluation metrics.

## Data and reproducibility

Uses the [UCI Individual Household Electric Power Consumption dataset](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption), licensed CC BY 4.0. The downloaded source file is not committed. Its SHA-256 for this run is \`4259c9d7ece5dbee9ab8d53682baac68d791c864f0f64a52b4043cb3b90894b7\`.

Download and run locally:

\`\`\`powershell
Invoke-WebRequest -Uri 'https://archive.ics.uci.edu/static/public/235/individual+household+electric+power+consumption.zip' -OutFile household_energy.zip
Expand-Archive household_energy.zip -DestinationPath data
python -m pip install -r requirements.txt
python main.py --input data/household_power_consumption.txt --out outputs
\`\`\`

## Evaluation

The 2,075,259 source rows were parsed into 409,887 observed five-minute means covering 2006-12-16 to 2010-11-26. Evaluation uses chronological 60/10/30 train, validation, and holdout partitions. A training-only 99th-percentile power threshold defines an *extreme-use proxy*; it is not a labeled equipment fault, safety incident, or ground-truth anomaly. A one-sided six-hour rolling median/MAD score is causal (the current reading is excluded). The threshold is selected on validation to target a 1% alert budget.

| Holdout measure | Result |
|---|---:|
| Extreme-use proxy prevalence | 0.53% |
| Alert rate | 1.26% |
| Precision against proxy | 5.02% |
| Recall against proxy | 11.93% |
| Average precision | 4.92% |
| ROC-AUC | 0.893 |

Ranking has signal against this narrow proxy, but the selected alert threshold captures only a modest share of proxy events and most alerts do not meet the extreme-use definition. Do not interpret alerts as evidence of equipment failure or unsafe conditions. The data represent one household; results do not establish generalization to other homes.

Aggregate metrics and source fingerprint: [\`reports/benchmark.json\`](reports/benchmark.json). No household-level readings or alert records are published. The code has no separate license file; UCI dataset attribution and CC BY 4.0 terms are retained.
