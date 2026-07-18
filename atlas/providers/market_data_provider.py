"""
Market Data Provider

Responsible for loading historical market data from disk.
Read-only provider. Does not download data or calculate indicators.
"""
import logging
from pathlib import Path
import pandas as pd

from atlas.config.settings import DAILY_DATA_DIR

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class DataNotFoundError(ProviderError):
    """Raised when data for a symbol cannot be found."""
    pass


class DataValidationError(ProviderError):
    """Raised when data fails validation."""
    pass


class MarketDataProvider:
    """
    Loads and validates historical market data from local CSV files.
    """
    
    REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]

    def __init__(self) -> None:
        """Initialize the MarketDataProvider."""
        pass

    def get(self, symbol: str) -> pd.DataFrame:
        """
        Get historical data for a single symbol.

        Args:
            symbol (str): The ticker symbol.

        Returns:
            pd.DataFrame: Validated historical data.

        Raises:
            DataNotFoundError: If the CSV file does not exist.
            DataValidationError: If the dataframe fails validation.
        """
        logger.info(f"Loading data for symbol: {symbol}")
        path = self._get_path(symbol)
        
        if not path.exists():
            logger.error(f"File not found for symbol: {symbol} at {path}")
            raise DataNotFoundError(f"Data for {symbol} not found at {path}")
            
        df = self._read_csv(path)
        df = self._prepare_dataframe(df)
        self._validate(df, symbol)
        
        return df

    def get_many(self, symbols: list[str]) -> dict[str, pd.DataFrame]:
        """
        Get historical data for multiple symbols.

        Args:
            symbols (list[str]): List of ticker symbols.

        Returns:
            dict[str, pd.DataFrame]: Dictionary mapping symbols to dataframes.
        """
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.get(symbol)
            except ProviderError as e:
                logger.warning(f"Failed to load {symbol}: {e}")
        return results

    def exists(self, symbol: str) -> bool:
        """
        Check if data exists for a symbol.

        Args:
            symbol (str): The ticker symbol.

        Returns:
            bool: True if data exists, False otherwise.
        """
        return self._get_path(symbol).exists()

    def list_symbols(self) -> list[str]:
        """
        List all available symbols with local data.

        Returns:
            list[str]: List of ticker symbols.
        """
        if not DAILY_DATA_DIR.exists():
            logger.warning(f"Data directory does not exist: {DAILY_DATA_DIR}")
            return []
            
        symbols = [f.stem for f in DAILY_DATA_DIR.glob("*.csv")]
        logger.debug(f"Found {len(symbols)} available symbols.")
        return sorted(symbols)

    def latest(self, symbol: str) -> pd.Series:
        """
        Get the latest row of data for a symbol.

        Args:
            symbol (str): The ticker symbol.

        Returns:
            pd.Series: The most recent row of data.

        Raises:
            DataNotFoundError: If data is not found.
            DataValidationError: If data fails validation.
        """
        df = self.get(symbol)
        return df.iloc[-1]

    def _get_path(self, symbol: str) -> Path:
        """
        Get the file path for a symbol's data.

        Args:
            symbol (str): The ticker symbol.

        Returns:
            Path: The full path to the CSV file.
        """
        return DAILY_DATA_DIR / f"{symbol}.csv"

    def _read_csv(self, path: Path) -> pd.DataFrame:
        """
        Read the CSV file into a dataframe.

        Args:
            path (Path): The path to the CSV file.

        Returns:
            pd.DataFrame: The loaded raw dataframe.
        """
        try:
            return pd.read_csv(path)
        except Exception as e:
            logger.error(f"Failed to read CSV at {path}: {e}")
            raise DataValidationError(f"Failed to read CSV: {e}")

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare the dataframe by converting types and removing duplicates.

        Args:
            df (pd.DataFrame): The raw dataframe.

        Returns:
            pd.DataFrame: The prepared dataframe.
        """
        if "Date" in df.columns:
            # Convert Date to datetime and handle potential errors
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
            # Drop rows where Date could not be parsed
            df = df.dropna(subset=["Date"])
            # Remove duplicate dates, keeping the last occurrence
            df = df.drop_duplicates(subset=["Date"], keep="last")
            # Sort in ascending order
            df = df.sort_values(by="Date", ascending=True)
            # Reset index
            df = df.reset_index(drop=True)
        return df

    def _validate(self, df: pd.DataFrame, symbol: str) -> None:
        """
        Validate the dataframe against required rules.

        Args:
            df (pd.DataFrame): The dataframe to validate.
            symbol (str): The ticker symbol (for error messages).

        Raises:
            DataValidationError: If any validation rule fails.
        """
        if df.empty:
            logger.error(f"Empty dataframe for {symbol}")
            raise DataValidationError(f"Data for {symbol} is empty.")

        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing columns for {symbol}: {missing_columns}")
            raise DataValidationError(f"Missing required columns: {missing_columns}")

        if not df["Date"].is_monotonic_increasing:
            logger.error(f"Dates are not in ascending order for {symbol}")
            raise DataValidationError("Dates are not in ascending order.")
