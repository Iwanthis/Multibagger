"""
Relative Volume Indicator

Provides the Relative Volume calculation (Volume / Rolling Average Volume).
"""
import logging
import pandas as pd

from atlas.indicators.base import Indicator

logger = logging.getLogger(__name__)


class RelativeVolumeIndicator(Indicator):
    """
    Relative Volume (RVOL) Indicator.
    """

    def __init__(self, period: int = 20) -> None:
        """
        Initialize the RelativeVolumeIndicator.

        Args:
            period (int): The lookback period for the rolling average. Defaults to 20.
        """
        self.period = period
        self.column_name = f"RVOL{self.period}"
        logger.debug(f"Initialized RelativeVolumeIndicator with period={self.period}")

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the RVOL and return a new dataframe.

        Args:
            data (pd.DataFrame): The input market data containing OHLCV columns.

        Returns:
            pd.DataFrame: A new dataframe with the RVOL column appended.
        """
        # Validate using the base class helper
        self._validate_dataframe(data)
        
        # Do not mutate the original dataframe
        df = data.copy()
        
        logger.info(f"Calculating {self.column_name}")
        
        # Calculate rolling average volume
        avg_volume = df["Volume"].rolling(window=self.period).mean()
        
        # Calculate Relative Volume
        df[self.column_name] = df["Volume"] / avg_volume
        
        return df
