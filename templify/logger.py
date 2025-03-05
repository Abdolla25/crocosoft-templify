import logging
import os

import yaml


def setup_logger():
    """Configure and return a logger instance."""
    # Load config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config["logging"]["level"]),
        format=config["logging"]["format"],
        handlers=[
            logging.FileHandler(config["logging"]["file"]),
            logging.StreamHandler(),
        ],
    )

    return logging.getLogger(__name__)
