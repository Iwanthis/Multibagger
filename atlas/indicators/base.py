"""
Base Indicator Framework

Provides the abstract base class and validation logic for all technical indicators.
Does not contain specific indicator math.
"""
from abc import ABC, abstractmethod
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class IndicatorValidationError(Exception):
    """Raised when the input dataframe fails validation for an indicator."""
    pass


class Indicator(ABC):
    """
    Abstract base class for all technical indicators.
    
    Every new indicator must inherit from this class and implement the
    `calculate` method.
    """
    
    REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]

    def _validate_dataframe(self, data: pd.DataFrame) -> None:
        """
        Validate the input dataframe to ensure it has data and required columns.
        
        Args:
            data (pd.DataFrame): The input market data.
            
        Raises:
            IndicatorValidationError: If the dataframe is empty or missing columns.
        """
        if data is None or data.empty:
            logger.error("Validation failed: Dataframe is empty.")
            raise IndicatorValidationError("Input dataframe cannot be empty.")
            
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in data.columns]
        if missing_columns:
            logger.error(f"Validation failed: Missing required columns: {missing_columns}")
            raise IndicatorValidationError(f"Missing required columns: {missing_columns}")
            
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the indicator values and append them to the dataframe.
        
        Args:
            data (pd.DataFrame): The input market data containing OHLCV columns.
            
        Returns:
            pd.DataFrame: The dataframe with the new indicator columns appended.
        """
        pass
