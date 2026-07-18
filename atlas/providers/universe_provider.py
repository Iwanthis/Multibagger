"""
Universe Provider

Responsible for loading stock universe lists from disk.
Does not download data or read market data.
"""
import logging
from pathlib import Path

import pandas as pd

from atlas.config.settings import UNIVERSE_DIR
from atlas.providers.market_data_provider import DataNotFoundError, DataValidationError

logger = logging.getLogger(__name__)


class UniverseProvider:
    """
    Loads and validates stock universe lists from local CSV files.
    """

    def __init__(self) -> None:
        """Initialize the UniverseProvider."""
        pass

    def _get_path(self, name: str) -> Path:
        """Get the local file path for a universe."""
        return UNIVERSE_DIR / f"{name}.csv"

    def get(self, name: str) -> list[str]:
        """
        Load a universe of symbols.

        Args:
            name (str): The universe name (e.g., 'nifty500').

        Returns:
            list[str]: A list of ticker symbols.

        Raises:
            DataNotFoundError: If the universe file does not exist.
            DataValidationError: If the file is invalid (e.g., missing 'Symbol' column).
        """
        path = self._get_path(name)
        
        if not path.exists():
            logger.error(f"Universe file not found: {path}")
            raise DataNotFoundError(f"Universe '{name}' not found at {path}")

        try:
            df = pd.read_csv(path)
        except Exception as e:
            logger.error(f"Failed to read universe CSV at {path}: {e}")
            raise DataValidationError(f"Failed to read universe '{name}': {e}")

        if "Symbol" not in df.columns:
            logger.error(f"Universe '{name}' missing 'Symbol' column.")
            raise DataValidationError(f"Universe '{name}' must contain a 'Symbol' column.")

        # Extract symbols, convert to string, drop NaNs (blank rows)
        symbols_series = df["Symbol"].dropna().astype(str)
        
        # Trim whitespace
        symbols_series = symbols_series.str.strip()
        
        # Drop empty strings after trimming
        symbols_series = symbols_series[symbols_series != ""]

        # Remove duplicates while preserving order
        # dict.fromkeys() is an idiomatic way in Python 3.7+ to remove duplicates and preserve order
        symbols = list(dict.fromkeys(symbols_series.tolist()))

        logger.info(f"Loaded {len(symbols)} symbols from universe '{name}'.")
        return symbols

    def list(self) -> list[str]:
        """
        List all available universes.

        Returns:
            list[str]: List of universe names.
        """
        if not UNIVERSE_DIR.exists():
            logger.warning(f"Universe directory does not exist: {UNIVERSE_DIR}")
            return []
            
        universes = [f.stem for f in UNIVERSE_DIR.glob("*.csv")]
        logger.debug(f"Found {len(universes)} available universes.")
        return sorted(universes)

    def exists(self, name: str) -> bool:
        """
        Check if a universe file exists.

        Args:
            name (str): The universe name.

        Returns:
            bool: True if it exists, False otherwise.
        """
        return self._get_path(name).exists()

    def count(self, name: str) -> int:
        """
        Get the number of symbols in a universe.

        Args:
            name (str): The universe name.

        Returns:
            int: The number of symbols.
        """
        symbols = self.get(name)
        return len(symbols)
