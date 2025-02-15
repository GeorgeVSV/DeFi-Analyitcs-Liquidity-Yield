"""Utility functions for DeFi Liquidity Tracker, including logging and error handling."""

import logging
import os
from typing import Dict

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def log_message(level: str, message: str) -> None:
    """Logs messages with specified level.

    Args:
        level (str): Log level (INFO, ERROR, WARNING).
        message (str): Log message.
    """
    if level == "INFO":
        logging.info(message)
    elif level == "ERROR":
        logging.error(message)
    elif level == "WARNING":
        logging.warning(message)
    else:
        logging.debug(message)

def format_currency(value: float, decimals: int = 2) -> str:
    """Formats numbers as human-readable currency.

    Args:
        value (float): Number to format.
        decimals (int): Decimal precision.

    Returns:
        str: Formatted currency string.
    """
    return f"${value:,.{decimals}f}"
