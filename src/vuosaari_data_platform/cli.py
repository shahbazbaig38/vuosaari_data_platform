"""Command-line entry point for the data pipeline."""

import logging

from vuosaari_data_platform.pipeline import run_pipeline


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    try:
        run_pipeline()
    except Exception:
        logging.exception("Pipeline failed")
        raise
