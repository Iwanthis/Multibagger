"""
VCP / Breakout Scanner

Filters for stocks displaying Volatility Contraction Pattern (VCP) characteristics,
evaluating only the latest available trading day.
"""
import logging
import pandas as pd

from atlas.scanners.base import Scanner, ScannerValidationError

logger = logging.getLogger(__name__)


class VCPScanner(Scanner):
    """
    Scans for VCP stocks based on trend alignment, proximity to highs, relative volume,
    and a measurable contraction in ATR relative to its recent history.
    """

    REQUIRED_COLUMNS = [
        "Close", "High", "Low", "ATR14", "RVOL20",
        "HIGH252", "EMA20", "EMA50", "EMA200"
    ]

    def __init__(
        self,
        high_proximity: float = 0.95,
        minimum_rvol: float = 1.20,
        atr_contraction: float = 0.80,
        lookback: int = 10
    ) -> None:
        """
        Initialize the VCP Scanner.

        Args:
            high_proximity (float): Minimum percentage of 52-week high required. Defaults to 0.95.
            minimum_rvol (float): Minimum relative volume threshold. Defaults to 1.20.
            atr_contraction (float): Maximum allowed current ATR relative to recent average. Defaults to 0.80.
            lookback (int): The number of prior days to average ATR over. Defaults to 10.
        """
        self.high_proximity = high_proximity
        self.minimum_rvol = minimum_rvol
        self.atr_contraction = atr_contraction
        self.lookback = lookback
        logger.debug(
            f"Initialized VCPScanner(high_prox={self.high_proximity}, "
            f"rvol={self.minimum_rvol}, atr_contr={self.atr_contraction}, "
            f"lookback={self.lookback})"
        )

    def scan(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluate the final row of the dataframe against VCP rules.

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
            logger.error(f"Missing required columns for VCPScanner: {missing}")
            raise ScannerValidationError(f"Missing required columns: {missing}")

        logger.info("Scanning for VCP pattern on the latest trading day...")
        
        if len(data) <= self.lookback:
            logger.warning("Insufficient history to calculate ATR contraction.")
            # Return empty dataframe maintaining columns and types
            return data.iloc[0:0].copy()

        # Isolate the final row for evaluation
        latest = data.tail(1).copy()
        
        # Calculate Previous Average ATR over `lookback` period (excluding the current row)
        # Slicing: from `-(lookback + 1)` up to `-1` (which excludes the final row)
        previous_atr = data["ATR14"].iloc[-(self.lookback + 1):-1]
        previous_avg_atr = previous_atr.mean()

        trend_aligned = (
            (latest["EMA20"] > latest["EMA50"]) &
            (latest["EMA50"] > latest["EMA200"]) &
            (latest["Close"] > latest["EMA20"])
        )
        
        near_high = latest["Close"] >= (latest["HIGH252"] * self.high_proximity)
        high_rvol = latest["RVOL20"] >= self.minimum_rvol
        
        # ATR Contraction: Current ATR <= Previous Avg ATR * threshold
        atr_contracted = latest["ATR14"] <= (previous_avg_atr * self.atr_contraction)
        
        condition = trend_aligned & near_high & high_rvol & atr_contracted
        
        # Apply mask
        matched = latest[condition].copy()
        
        if not matched.empty:
            logger.info("VCP scan passed.")
        else:
            logger.info("VCP scan failed.")
            
        return matched
