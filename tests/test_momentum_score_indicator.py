import pandas as pd
import pytest

from atlas.indicators.momentum_score import MomentumScoreIndicator
from atlas.indicators.base import IndicatorValidationError


@pytest.fixture
def sample_data():
    """Provides deterministic sample data containing all required columns."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=5),
        "Open": [10.0] * 5,
        "High": [12.0] * 5,
        "Low": [8.0] * 5,
        "Close": [10.0, 10.0, 10.0, 10.0, 10.0],
        "Volume": [1000] * 5,
        "RVOL20": [1.0, 5.0, 12.0, 1.0, 1.0],  # 12.0 should cap at 100 score
        "RS90": [0.0, 0.25, 0.5, 0.75, 1.0],   # Min=0.0, Max=1.0 for easy normalization
        "HIGH252": [20.0, 20.0, 20.0, 20.0, 20.0]
    })


def test_momentum_score_calculation(sample_data):
    indicator = MomentumScoreIndicator()
    result = indicator.calculate(sample_data)
    
    assert "MomentumScore" in result.columns
    
    # Day 0: 
    # Close=10, High252=20 -> HighScore = (10/20)*100 = 50. 50 * 0.30 = 15.0
    # RVOL=1.0 -> RVOLScore = 1.0 * 10 = 10. 10 * 0.20 = 2.0
    # RS90=0.0 -> Normalizes to 0. 0 * 0.50 = 0
    # Total = 15.0 + 2.0 + 0 = 17.0
    assert result["MomentumScore"].iloc[0] == pytest.approx(17.0)
    
    # Day 2:
    # HighScore = 50 * 0.30 = 15.0
    # RVOL=12.0 -> RVOLScore = 120, capped at 100. 100 * 0.20 = 20.0
    # RS90=0.5 -> Normalizes to 50. 50 * 0.50 = 25.0
    # Total = 15.0 + 20.0 + 25.0 = 60.0
    assert result["MomentumScore"].iloc[2] == pytest.approx(60.0)
    
    # Day 4:
    # HighScore = 50 * 0.30 = 15.0
    # RVOL=1.0 -> 10 * 0.20 = 2.0
    # RS90=1.0 -> Normalizes to 100. 100 * 0.50 = 50.0
    # Total = 15.0 + 2.0 + 50.0 = 67.0
    assert result["MomentumScore"].iloc[4] == pytest.approx(67.0)


def test_missing_indicator_columns(sample_data):
    # Drop one of the required indicator columns
    df = sample_data.drop(columns=["RVOL20"])
    
    indicator = MomentumScoreIndicator()
    with pytest.raises(IndicatorValidationError, match="Missing required columns"):
        indicator.calculate(df)


def test_original_dataframe_unchanged(sample_data):
    original_columns = list(sample_data.columns)
    
    indicator = MomentumScoreIndicator()
    indicator.calculate(sample_data)
    
    assert list(sample_data.columns) == original_columns
    assert "MomentumScore" not in sample_data.columns


def test_score_bounds(sample_data):
    # Setup data that maxes out all scores
    df = sample_data.copy()
    # HighScore = (10 / 10) * 100 = 100
    df["HIGH252"] = 10.0
    df["Close"] = 10.0
    # RVOLScore = 15 * 10 = 150 -> capped at 100
    df["RVOL20"] = 15.0
    # RS90 Max = 100 normalization
    df["RS90"] = [0.0, 0.0, 0.0, 0.0, 1.0] # Index 4 gets normalized to 100
    
    indicator = MomentumScoreIndicator()
    result = indicator.calculate(df)
    
    # Index 4 should be 100 total
    assert result["MomentumScore"].iloc[4] == pytest.approx(100.0)
    
    # Check that all values are between 0 and 100
    assert (result["MomentumScore"] >= 0).all()
    assert (result["MomentumScore"] <= 100).all()


def test_flat_rs(sample_data):
    # RS is identical everywhere, min == max
    df = sample_data.copy()
    df["RS90"] = 0.5
    
    indicator = MomentumScoreIndicator()
    result = indicator.calculate(df)
    
    # If min == max, rs_score should be 0 safely without div-by-zero
    # Day 0: HighScore=15.0, RVOLScore=2.0, RSScore=0 -> 17.0
    assert result["MomentumScore"].iloc[0] == pytest.approx(17.0)


def test_empty_dataframe():
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "RVOL20", "RS90", "HIGH252"])
    
    indicator = MomentumScoreIndicator()
    with pytest.raises(IndicatorValidationError, match="cannot be empty"):
        indicator.calculate(df)
