"""
Momentum Score Indicator

Calculates an overall momentum score by combining RS90, HighScore, and RVOLScore.
"""
import logging
import pandas as pd

from atlas.indicators.base import Indicator, IndicatorValidationError

logger = logging.getLogger(__name__)


class MomentumScoreIndicator(Indicator):
    """
    Momentum Score Indicator.
    Combines Relative Strength, Distance from 52-week High, and Relative Volume
    into a single 0-100 score.
    """
    
    # Extend the base required columns with the indicators needed for the score
    REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume", "RVOL20", "RS90", "HIGH252"]

    def __init__(self) -> None:
        """Initialize the MomentumScoreIndicator."""
        self.column_name = "MomentumScore"
        logger.debug("Initialized MomentumScoreIndicator")

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the Momentum Score and return a new dataframe.

        Args:
            data (pd.DataFrame): The input market data containing OHLCV and required indicator columns.

        Returns:
            pd.DataFrame: A new dataframe with the MomentumScore column appended.
        """
        # Validate using the base class helper (will use the overridden REQUIRED_COLUMNS)
        self._validate_dataframe(data)
        
        # Do not mutate the original dataframe
        df = data.copy()
        
        logger.info(f"Calculating {self.column_name}")
        
        # 1. High Score: Distance from High
        # DistanceFromHigh = Close / HIGH252
        # HighScore = DistanceFromHigh * 100
        high_score = (df["Close"] / df["HIGH252"]) * 100
        
        # 2. RVOL Score: RVOL20 * 10, capped at 100
        rvol_score = df["RVOL20"] * 10
        rvol_score = rvol_score.clip(upper=100)
        
        # 3. RS Score: Min-Max normalization of RS90 to 0-100
        rs = df["RS90"]
        rs_min = rs.min()
        rs_max = rs.max()
        
        if rs_max == rs_min:
            # Prevent division by zero if RS is completely flat
            rs_score = pd.Series(0, index=df.index)
        else:
            rs_score = ((rs - rs_min) / (rs_max - rs_min)) * 100
            
        # 4. Overall Momentum Score
        # 0.50 * RSScore + 0.30 * HighScore + 0.20 * RVOLScore
        momentum_score = (0.50 * rs_score) + (0.30 * high_score) + (0.20 * rvol_score)
        
        df[self.column_name] = momentum_score
        
        return df
