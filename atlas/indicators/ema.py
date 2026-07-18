"""
EMA Indicator

Provides the Exponential Moving Average calculation.
"""
import logging
import pandas as pd

from atlas.indicators.base import Indicator

logger = logging.getLogger(__name__)


class EMAIndicator(Indicator):
    """
    Exponential Moving Average (EMA) Indicator.
    """

    def __init__(self, period: int = 20) -> None:
        """
        Initialize the EMAIndicator.

        Args:
            period (int): The period for the EMA calculation. Defaults to 20.
        """
        self.period = period
        self.column_name = f"EMA{self.period}"
        logger.debug(f"Initialized EMAIndicator with period={self.period}")

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the EMA and return a new dataframe.

        Args:
            data (pd.DataFrame): The input market data containing OHLCV columns.

        Returns:
            pd.DataFrame: A new dataframe with the EMA column appended.
        """
        # Validate using the base class helper
        self._validate_dataframe(data)
        
        # Do not mutate the original dataframe
        df = data.copy()
        
        logger.info(f"Calculating {self.column_name}")
        
        # Calculate EMA using span=period and adjust=False
        df[self.column_name] = df["Close"].ewm(span=self.period, adjust=False).mean()
        
        return df
