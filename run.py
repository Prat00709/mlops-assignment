import argparse
import json
import time
import logging
import pandas as pd
import yaml
import numpy as np
import sys

def load_config(config_path):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


def validate_config(config):
    required_fields = [
        "seed",
        "window",
        "version"
    ]

    for field in required_fields:
        if field not in config:
            raise ValueError(
                f"Missing config field: {field}"
            )


def load_dataset(input_path):
    df = pd.read_csv(input_path)

    # Handle malformed CSV where everything is stored in one column
    if len(df.columns) == 1:
        single_col = df.columns[0]

        expanded = df[single_col].str.split(",", expand=True)

        expanded.columns = single_col.split(",")

        df = expanded

    return df


def validate_dataset(df):
    if df.empty:
        raise ValueError("Dataset is empty")

    if "close" not in df.columns:
        raise ValueError(
            "Missing required column: close"
        )


def calculate_rolling_mean(df, window):
    df["rolling_mean"] = (
        df["close"]
        .astype(float)
        .rolling(window=window)
        .mean()
    )

    return df

def generate_signal(df):
    df["signal"] = (
        df["close"].astype(float)
        > df["rolling_mean"]
    )

    df["signal"] = df["signal"].astype(float)

    df.loc[
        df["rolling_mean"].isna(),
        "signal"
    ] = float("nan")

    return df


def write_metrics(metrics, output_path):
    with open(output_path, "w") as file:
        json.dump(metrics, file, indent=4)

def setup_logging(log_file):

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args = parser.parse_args()
    setup_logging(args.log_file)
    logging.info("Job Started")

    try:

        start_time = time.time()

        config = load_config(args.config)

        validate_config(config)

        np.random.seed(config["seed"])

        logging.info(f"Random seed set to {config['seed']}")

        logging.info(f"Config validated | seed={config['seed']} | window={config['window']} | version={config['version']}")

        df = load_dataset(args.input)

        validate_dataset(df)
        logging.info(f"Rows loaded: {len(df)}")

        logging.info("Calculating rolling mean")

        df = calculate_rolling_mean(
            df,
            config["window"]
        )

        logging.info("Rolling mean calculation completed")

        logging.info("Generating signals")

        df = generate_signal(df)

        logging.info("Signal generation completed")

        latency_ms = round(
            (time.time() - start_time) * 1000,
            2
        )

        rows_processed = len(df)

        signal_rate = float(
            round(
                df["signal"].mean(),
                4
            )
        )

        metrics = {
            "version": config["version"],
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": signal_rate,
            "latency_ms": latency_ms,
            "seed": config["seed"],
            "status": "success"
        }

        logging.info(f"Metrics Summary | rows={rows_processed} | signal_rate={signal_rate} | latency_ms={latency_ms}")

        write_metrics(
            metrics,
            args.output
        )

        logging.info("Job completed successfully")

        print(metrics)

    except Exception as e:

        logging.exception("Pipeline failed")

        error_metrics = {
            "version": "v1",
            "status": "error",
            "error_message": str(e)
        }

        write_metrics(
            error_metrics,
            args.output
        )

        print(error_metrics)
        sys.exit(1)

if __name__ == "__main__":
    main()