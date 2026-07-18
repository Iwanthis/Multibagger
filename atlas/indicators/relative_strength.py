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
        
        if len(data) != len(benchmark_data):
            logger.error(f"Length mismatch: data length {len(data)}, benchmark length {len(benchmark_data)}")
            raise IndicatorValidationError("Stock data and benchmark data must have equal length.")
            
        # Ensure Dates align precisely row by row
        if not (data["Date"].reset_index(drop=True) == benchmark_data["Date"].reset_index(drop=True)).all():
            logger.error("Date mismatch between stock data and benchmark data.")
            raise IndicatorValidationError("Stock data and benchmark data must align by Date.")
        
        # Do not mutate the original dataframe
        df = data.copy()
        
        logger.info(f"Calculating {self.column_name}")
        
        # Calculate returns
        stock_return = (df["Close"] / df["Close"].shift(self.period)) - 1
        
        # Reset index on benchmark to ensure perfect alignment when doing math
        bench_close = benchmark_data["Close"].reset_index(drop=True)
        benchmark_return = (bench_close / bench_close.shift(self.period)) - 1
        
        # Align stock returns using reset index to avoid index mismatch errors
        stock_return = stock_return.reset_index(drop=True)
        rs = stock_return - benchmark_return
        
        # Assign back using original index
        rs.index = df.index
        df[self.column_name] = rs
        
        return df
