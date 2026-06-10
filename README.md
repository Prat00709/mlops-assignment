# MLOps Assignment

## Overview

This project implements a simple MLOps pipeline that processes cryptocurrency market data, calculates a rolling mean on the `close` price column, generates trading signals, and outputs performance metrics in JSON format.

The solution includes:

* Configuration management using YAML
* Data validation
* Rolling mean calculation
* Signal generation
* Metrics reporting
* Error handling
* Logging
* Docker containerization
* Reproducibility through random seed configuration

---

## Project Structure

```text
.
├── run.py
├── config.yaml
├── data.csv
├── requirements.txt
├── Dockerfile
├── README.md
└── .dockerignore
```

---

## Configuration

Example `config.yaml`:

```yaml
seed: 42
window: 5
version: "v1"
```

---

## Metrics Output

Example success output:

```json
{
    "version": "v1",
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.4991,
    "latency_ms": 42.54,
    "seed": 42,
    "status": "success"
}
```

Example error output:

```json
{
    "version": "v1",
    "status": "error",
    "error_message": "Description of error"
}
```

---

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log

---

## Docker

Build image:

```bash
docker build -t mlops-task .
```

Run container:

```bash
docker run --rm mlops-task
```

---

## Logging

The pipeline logs:

* Job start
* Configuration validation
* Dataset loading
* Rolling mean calculation
* Signal generation
* Metrics summary
* Job completion
* Exceptions

Logs are written to `run.log`.

---

## Assumptions

* Only the `close` column is used for calculations.
* The first `window - 1` rows have insufficient data for rolling mean calculation and therefore produce `NaN` values.
* Rows with `NaN` signals are excluded from signal rate calculation.
* Input files must contain a `close` column.
* Empty datasets are treated as errors.

```
```

