# Household Energy Anomaly Watch

Detect sustained household electricity outliers with a rolling robust baseline and actionable event export.

> **Portfolio prototype.** Source code is provided; no benchmark results are claimed until you run it on the cited data and record the output.

## Use case

Detect sustained household electricity outliers with a rolling robust baseline and actionable event export. The CLI consumes local files, emits reproducible reports, and keeps data out of the repository.

## Data and provenance

[UCI Individual Household Electric Power Consumption (CC BY 4.0)](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption). The UCI semicolon-delimited source file, with Date, Time, and Global_active_power columns. Source files are not bundled. Respect source terms and cite the dataset when publishing results.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Download/prepare the source data locally, then run:
python main.py --input data/household_power_consumption.txt --out outputs
```

## Outputs

Generated results are saved under `outputs/`; file names and metrics are printed or documented by the CLI. The repository excludes downloaded data and artifacts.

## Evaluation and operating notes

A single household's historical profile is not a general energy baseline. Missing values are excluded; alerts are statistical review candidates, not evidence of equipment failure.

For production use, add a frozen reference period, out-of-time evaluation, monitoring ownership, and a documented rollback or escalation path. This project is a local baseline, not a deployed service.

## License

No code license file is included yet. Third-party data remains subject to its source terms.
