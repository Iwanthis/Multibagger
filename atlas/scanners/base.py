"""
Base Scanner Framework

Provides the abstract base class and validation logic for all momentum scanners.
Does not contain specific scanner rules.
"""
from abc import ABC, abstractmethod
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class ScannerValidationError(Exception):
    """Raised when the input dataframe fails validation for a scanner."""
    pass


class Scanner(ABC):
    """
    Abstract base class for all scanners.
    
    Every new scanner must inherit from this class and implement the
    `scan` method.
    """

    def _validate(self, data: pd.DataFrame) -> None:
        """
        Validate the input dataframe to ensure it has data.
        
        Args:
            data (pd.DataFrame): The input market data with indicators.
            
        Raises:
            ScannerValidationError: If the dataframe is empty.
        """
        if data is None or data.empty:
            logger.error("Scanner validation failed: Dataframe is empty.")
            raise ScannerValidationError("Input dataframe cannot be empty.")
            
    @abstractmethod
    def scan(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluate the dataframe against scanner rules.
        
        Args:
            data (pd.DataFrame): The input market data with indicators.
            
        Returns:
            pd.DataFrame: A dataframe containing only the rows that satisfy the rules.
        """
        pass

    def scan_latest(self, data: pd.DataFrame) -> bool:
        """
        Evaluate if the latest trading day satisfies the scanner rules.
        
        Args:
            data (pd.DataFrame): The input market data.
            
        Returns:
            bool: True if the latest day satisfies the rules, False otherwise.
        """
        self._validate(data)
        latest_row_df = data.iloc[[-1]].copy()
        matched = self.scan(latest_row_df)
        return not matched.empty
