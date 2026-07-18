"""
Download Manager

Responsible for downloading historical OHLCV data from Yahoo Finance and saving it locally.
Read-only provider for the rest of the application. Does not calculate indicators or hold business logic.
"""
import logging
from pathlib import Path

import pandas as pd
import yfinance as yf

from atlas.config.settings import DAILY_DATA_DIR
from atlas.providers.market_data_provider import ProviderError

logger = logging.getLogger(__name__)


class DownloadError(ProviderError):
    """Raised when downloading data fails."""
    pass


class DownloadManager:
    """
    Downloads and stores historical market data using yfinance.
    """

    REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]

    def __init__(self) -> None:
        """Initialize the DownloadManager."""
        pass

    def _get_path(self, symbol: str) -> Path:
        """Get the local file path for a symbol's data."""
        return DAILY_DATA_DIR / f"{symbol}.csv"

    def download(self, symbol: str, period: str = "5y") -> Path:
        """
        Download historical data for a single symbol.

        Args:
            symbol (str): The ticker symbol (e.g., 'RELIANCE').
            period (str): The historical period to download (default: '5y').

        Returns:
            Path: The path to the saved CSV file.

        Raises:
            DownloadError: If the download fails or returns invalid data.
        """
        # Automatically append .NS for Indian stocks if not present, unless it's an index (starts with ^)
        if symbol.startswith("^"):
            fetch_symbol = symbol
        else:
            fetch_symbol = f"{symbol}.NS" if not symbol.endswith(".NS") else symbol
        # Ensure save file does not contain .NS
        save_symbol = symbol.replace(".NS", "") if symbol.endswith(".NS") else symbol
        
        logger.info(f"Downloading {period} data for {fetch_symbol}")
        
        try:
            df = yf.download(fetch_symbol, period=period, progress=False)
        except Exception as e:
            logger.error(f"Failed to fetch {fetch_symbol}: {e}")
            raise DownloadError(f"Download failed for {symbol}: {e}")

        if df.empty:
            logger.error(f"Downloaded empty dataframe for {fetch_symbol}")
            raise DownloadError(f"No data returned for {symbol}")

        # Flatten MultiIndex columns (common in newer yfinance versions)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Reset index to turn 'Date' (or 'Datetime') into a regular column
        df = df.reset_index()

        # Rename 'Datetime' to 'Date' if necessary (happens for intraday or some yf versions)
        if "Datetime" in df.columns and "Date" not in df.columns:
            df = df.rename(columns={"Datetime": "Date"})

        # Validate required columns
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            logger.error(f"Missing required columns from download for {symbol}: {missing}")
            raise DownloadError(f"Missing columns in downloaded data: {missing}")

        # Keep only required columns in a fixed order
        df = df[self.REQUIRED_COLUMNS]

        # Ensure target directory exists
        DAILY_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        save_path = self._get_path(save_symbol)
        try:
            # Save as CSV, overwriting if it exists
            df.to_csv(save_path, index=False)
            logger.info(f"Saved {len(df)} rows to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save {save_symbol} to {save_path}: {e}")
            raise DownloadError(f"Failed to save data: {e}")

        return save_path

    def download_many(self, symbols: list[str], period: str = "5y") -> dict[str, bool]:
        """
        Download historical data for multiple symbols.

        Args:
            symbols (list[str]): List of ticker symbols.
            period (str): The historical period to download (default: '5y').

        Returns:
            dict[str, bool]: Dictionary mapping symbols to success status (True/False).
        """
        results = {}
        for symbol in symbols:
            try:
                self.download(symbol, period=period)
                results[symbol] = True
            except DownloadError as e:
                logger.warning(f"Download failed for {symbol}: {e}")
                results[symbol] = False
        return results

    def refresh(self, symbol: str) -> Path:
        """
        Refresh data for a symbol by overwriting it with a new download.

        Args:
            symbol (str): The ticker symbol.

        Returns:
            Path: The path to the saved CSV file.
        """
        return self.download(symbol, period="5y")
