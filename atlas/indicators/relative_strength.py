"""
Relative Strength Indicator

Provides the Relative Strength (RS) calculation comparing a stock's return
against a benchmark's return over a specified period.
"""
import logging
import pandas as pd

from atlas.indicators.base import Indicator, IndicatorValidationError

logger = logging.getLogger(__name__)


class RelativeStrengthIndicator(Indicator):
    """
    Relative Strength Indicator.
    Compares the percentage return of a stock against a benchmark over a period.
    """

    def __init__(self, period: int = 90) -> None:
        """
        Initialize the RelativeStrengthIndicator.

        Args:
            period (int): The lookback period in days for the return calculation. Defaults to 90.
        """
        self.period = period
        self.column_name = f"RS{self.period}"
        logger.debug(f"Initialized RelativeStrengthIndicator with period={self.period}")

    def calculate(self, data: pd.DataFrame, benchmark_data: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate the Relative Strength and return a new dataframe.

        Args:
            data (pd.DataFrame): The input stock market data containing OHLCV columns.
            benchmark_data (pd.DataFrame): The input benchmark market data containing OHLCV columns.

        Returns:
            pd.DataFrame: A new dataframe with the RS column appended.
            
        Raises:
            IndicatorValidationError: If data is invalid, lengths do not match, or dates do not align.
        """
        if benchmark_data is None:
            raise IndicatorValidationError("benchmark_data must be provided for RelativeStrengthIndicator")

        # Validate both dataframes using the base class helper
        self._validate_dataframe(data)
        self._validate_dataframe(benchmark_data)
        
        # Do not mutate the original dataframe
        df = data.copy()
        
        # Align using INNER JOIN on Date
        aligned = pd.merge(
            df[["Date", "Close"]], 
            benchmark_data[["Date", "Close"]], 
            on="Date", 
            how="inner", 
            suffixes=("_stock", "_bench")
        )
        
        # Verify sufficient common trading dates
        if len(aligned) < (self.period + 1):
            raise IndicatorValidationError(
                f"Not enough common trading dates. Need {self.period + 1}, got {len(aligned)}"
            )
            
        logger.info(f"Calculating {self.column_name}")
        
        # Calculate returns on aligned data
        stock_return = (aligned["Close_stock"] / aligned["Close_stock"].shift(self.period)) - 1
        benchmark_return = (aligned["Close_bench"] / aligned["Close_bench"].shift(self.period)) - 1
        aligned[self.column_name] = stock_return - benchmark_return
        
        # Merge RS back to the original dataframe preserving its shape
        df = pd.merge(df, aligned[["Date", self.column_name]], on="Date", how="left")
        
        return df
