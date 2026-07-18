"""
High/Low Indicator

Provides the rolling highest high and lowest low calculation over a specified period
(e.g., 52-week high/low using 252 trading days).
"""
import logging
import pandas as pd

from atlas.indicators.base import Indicator

logger = logging.getLogger(__name__)


class HighLowIndicator(Indicator):
    """
    High/Low Indicator.
    Calculates the rolling maximum high and rolling minimum low over a period.
    """

    def __init__(self, period: int = 252) -> None:
        """
        Initialize the HighLowIndicator.

        Args:
            period (int): The lookback period in trading days. Defaults to 252 (approx 52 weeks).
        """
        self.period = period
        self.high_col = f"HIGH{self.period}"
        self.low_col = f"LOW{self.period}"
        logger.debug(f"Initialized HighLowIndicator with period={self.period}")

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the rolling High/Low and return a new dataframe.

        Args:
            data (pd.DataFrame): The input market data containing OHLCV columns.

        Returns:
            pd.DataFrame: A new dataframe with the HIGH and LOW columns appended.
        """
        # Validate using the base class helper
        self._validate_dataframe(data)
        
        # Do not mutate the original dataframe
        df = data.copy()
        
        logger.info(f"Calculating {self.high_col} and {self.low_col}")
        
        # Calculate rolling highest high
        df[self.high_col] = df["High"].rolling(window=self.period).max()
        
        # Calculate rolling lowest low
        df[self.low_col] = df["Low"].rolling(window=self.period).min()
        
        return df
