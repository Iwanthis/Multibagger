"""
Institutional Buying Scanner

Filters for stocks displaying strong institutional accumulation characteristics.
Evaluates price action relative to volume and volatility.
"""
import logging
import pandas as pd
import numpy as np

from atlas.scanners.base import Scanner, ScannerValidationError

logger = logging.getLogger(__name__)


class InstitutionalScanner(Scanner):
    """
    Scans for institutional buying activity based on body size, ATR expansion,
    and relative volume.
    """

    REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "ATR14", "RVOL20"]

    def __init__(
        self,
        rvol_threshold: float = 2.0,
        body_threshold: float = 0.60,
        atr_multiplier: float = 1.0
    ) -> None:
        """
        Initialize the Institutional Scanner.

        Args:
            rvol_threshold (float): Minimum relative volume threshold. Defaults to 2.0.
            body_threshold (float): Minimum body percentage of total range. Defaults to 0.60.
            atr_multiplier (float): Minimum range expansion relative to ATR. Defaults to 1.0.
        """
        self.rvol_threshold = rvol_threshold
        self.body_threshold = body_threshold
        self.atr_multiplier = atr_multiplier
        logger.debug(
            f"Initialized InstitutionalScanner(rvol={self.rvol_threshold}, "
            f"body={self.body_threshold}, atr={self.atr_multiplier})"
        )

    def scan(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the dataframe for institutional buying patterns.

        Args:
            data (pd.DataFrame): The input market data containing required indicators.

        Returns:
            pd.DataFrame: A new dataframe containing only the matching rows.
            
        Raises:
            ScannerValidationError: If the dataframe is empty or missing required columns.
        """
        # Base validation (empty check)
        self._validate(data)
        
        # Check required columns
        missing = [col for col in self.REQUIRED_COLUMNS if col not in data.columns]
        if missing:
            logger.error(f"Missing required columns for InstitutionalScanner: {missing}")
            raise ScannerValidationError(f"Missing required columns: {missing}")

        logger.info("Scanning for institutional accumulation...")
        
        # Calculate components using vectorization
        body = (data["Close"] - data["Open"]).abs()
        range_high_low = data["High"] - data["Low"]
        
        # Prevent division by zero if range is 0 (e.g. upper/lower circuits or flat trading)
        body_pct = np.where(range_high_low == 0, 0, body / range_high_low)
        
        # Evaluate rules
        bullish = data["Close"] > data["Open"]
        atr_expansion = range_high_low > (data["ATR14"] * self.atr_multiplier)
        high_rvol = data["RVOL20"] >= self.rvol_threshold
        strong_body = body_pct >= self.body_threshold
        
        # Combine conditions
        condition = bullish & atr_expansion & high_rvol & strong_body
        
        # Return only matching rows
        matched = data[condition].copy()
        
        logger.info(f"Scan complete. Found {len(matched)} matching rows.")
        return matched
