"""
Momentum Scanner

Filters for stocks displaying strong upward momentum characteristics, evaluating
only the latest available trading day.
"""
import logging
import pandas as pd

from atlas.scanners.base import Scanner, ScannerValidationError

logger = logging.getLogger(__name__)


class MomentumScanner(Scanner):
    """
    Scans for momentum stocks based on moving average alignment, relative volume,
    proximity to 52-week highs, and a composite momentum score.
    """

    REQUIRED_COLUMNS = [
        "Close", "EMA20", "EMA50", "EMA200", 
        "HIGH252", "RVOL20", "MomentumScore"
    ]

    def __init__(
        self,
        minimum_score: float = 70.0,
        minimum_rvol: float = 1.20,
        high_proximity: float = 0.95
    ) -> None:
        """
        Initialize the Momentum Scanner.

        Args:
            minimum_score (float): Minimum required Momentum Score. Defaults to 70.0.
            minimum_rvol (float): Minimum relative volume threshold. Defaults to 1.20.
            high_proximity (float): Minimum percentage of 52-week high required (e.g. 0.95 = within 5%). Defaults to 0.95.
        """
        self.minimum_score = minimum_score
        self.minimum_rvol = minimum_rvol
        self.high_proximity = high_proximity
        logger.debug(
            f"Initialized MomentumScanner(score={self.minimum_score}, "
            f"rvol={self.minimum_rvol}, high_prox={self.high_proximity})"
        )

    def scan(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluate the final row of the dataframe against momentum rules.

        Args:
            data (pd.DataFrame): The input market data containing required indicators.

        Returns:
            pd.DataFrame: A new dataframe containing the single latest row if it passes,
                          otherwise an empty dataframe.
            
        Raises:
            ScannerValidationError: If the dataframe is empty or missing required columns.
        """
        self._validate(data)
        
        missing = [col for col in self.REQUIRED_COLUMNS if col not in data.columns]
        if missing:
            logger.error(f"Missing required columns for MomentumScanner: {missing}")
            raise ScannerValidationError(f"Missing required columns: {missing}")

        logger.info("Scanning for momentum on the latest trading day...")
        
        # Isolate the final row as a 1-row DataFrame to preserve shape and column types
        latest = data.tail(1).copy()
        
        # Evaluate rules natively on the 1-row DataFrame
        trend_aligned = (
            (latest["Close"] > latest["EMA20"]) &
            (latest["EMA20"] > latest["EMA50"]) &
            (latest["EMA50"] > latest["EMA200"])
        )
        
        high_rvol = latest["RVOL20"] >= self.minimum_rvol
        near_high = latest["Close"] >= (latest["HIGH252"] * self.high_proximity)
        strong_momentum = latest["MomentumScore"] >= self.minimum_score
        
        condition = trend_aligned & high_rvol & near_high & strong_momentum
        
        # Apply mask to return the row if true, else empty dataframe
        matched = latest[condition].copy()
        
        if not matched.empty:
            logger.info("Momentum scan passed.")
        else:
            logger.info("Momentum scan failed.")
            
        return matched
