"""
ATR Indicator

Provides the Average True Range calculation.
"""
import logging
import pandas as pd

from atlas.indicators.base import Indicator

logger = logging.getLogger(__name__)


class ATRIndicator(Indicator):
    """
    Average True Range (ATR) Indicator using Wilder's smoothing.
    """

    def __init__(self, period: int = 14) -> None:
        """
        Initialize the ATRIndicator.

        Args:
            period (int): The period for the ATR calculation. Defaults to 14.
        """
        self.period = period
        self.column_name = f"ATR{self.period}"
        logger.debug(f"Initialized ATRIndicator with period={self.period}")

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the ATR and return a new dataframe.

        Args:
            data (pd.DataFrame): The input market data containing OHLCV columns.

        Returns:
            pd.DataFrame: A new dataframe with the ATR column appended.
        """
        # Validate using the base class helper
        self._validate_dataframe(data)
        
        # Do not mutate the original dataframe
        df = data.copy()
        
        logger.info(f"Calculating {self.column_name}")
        
        # Calculate True Range (TR)
        prev_close = df["Close"].shift(1)
        tr1 = df["High"] - df["Low"]
        tr2 = (df["High"] - prev_close).abs()
        tr3 = (df["Low"] - prev_close).abs()
        
        # max(axis=1) will automatically ignore NaNs for the first row
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR using Wilder's smoothing (alpha = 1/period)
        df[self.column_name] = tr.ewm(alpha=1/self.period, adjust=False).mean()
        
        return df
