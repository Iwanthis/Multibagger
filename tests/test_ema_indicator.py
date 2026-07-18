import pandas as pd
import pytest

from atlas.indicators.ema import EMAIndicator
from atlas.indicators.base import IndicatorValidationError


@pytest.fixture
def sample_data():
    """Provides deterministic sample data for testing."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=5),
        "Open": [10.0, 11.0, 12.0, 13.0, 14.0],
        "High": [11.0, 12.0, 13.0, 14.0, 15.0],
        "Low": [9.0, 10.0, 11.0, 12.0, 13.0],
        "Close": [10.0, 10.5, 11.0, 11.5, 12.0],
        "Volume": [1000, 1100, 1200, 1300, 1400]
    })


def test_ema20_calculation(sample_data):
    indicator = EMAIndicator(period=20)
    result = indicator.calculate(sample_data)
    
    assert "EMA20" in result.columns
    # Check that it computes an EWM correctly. 
    # For period=20, alpha = 2/(20+1) = 2/21 = 0.095238
    # First value should equal first close
    assert result["EMA20"].iloc[0] == 10.0
    # Second value: 10 + (10.5 - 10) * (2/21) = 10 + 0.047619 = 10.047619
    assert result["EMA20"].iloc[1] == pytest.approx(10.047619, rel=1e-5)


def test_ema50_calculation(sample_data):
    indicator = EMAIndicator(period=50)
    result = indicator.calculate(sample_data)
    
    assert "EMA50" in result.columns
    # For period=50, alpha = 2/(50+1) = 2/51 = 0.039215
    assert result["EMA50"].iloc[0] == 10.0
    # Second value: 10 + 0.5 * (2/51) = 10 + 0.0196078 = 10.0196078
    assert result["EMA50"].iloc[1] == pytest.approx(10.0196078, rel=1e-5)


def test_original_dataframe_unchanged(sample_data):
    original_columns = list(sample_data.columns)
    
    indicator = EMAIndicator(period=20)
    indicator.calculate(sample_data)
    
    # Original should still have exactly the same columns
    assert list(sample_data.columns) == original_columns
    assert "EMA20" not in sample_data.columns


def test_missing_columns():
    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=2),
        "Close": [10.0, 11.0]
    })
    
    indicator = EMAIndicator()
    with pytest.raises(IndicatorValidationError, match="Missing required columns"):
        indicator.calculate(df)


def test_empty_dataframe():
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    
    indicator = EMAIndicator()
    with pytest.raises(IndicatorValidationError, match="cannot be empty"):
        indicator.calculate(df)


def test_output_properties(sample_data):
    indicator = EMAIndicator(period=20)
    result = indicator.calculate(sample_data)
    
    # Ensure row count is unchanged
    assert len(result) == len(sample_data)
    
    # Ensure EMA20 column exists
    assert "EMA20" in result.columns
