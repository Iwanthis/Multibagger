import pandas as pd
import pytest

from atlas.indicators.atr import ATRIndicator
from atlas.indicators.base import IndicatorValidationError


@pytest.fixture
def sample_data():
    """Provides deterministic sample data for testing."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=5),
        "Open": [10.0, 11.0, 12.0, 13.0, 14.0],
        "High": [12.0, 13.0, 14.0, 15.0, 16.0],
        "Low": [8.0, 9.0, 10.0, 11.0, 12.0],
        "Close": [11.0, 12.0, 13.0, 14.0, 15.0],
        "Volume": [1000, 1100, 1200, 1300, 1400]
    })


def test_atr14_calculation(sample_data):
    indicator = ATRIndicator(period=14)
    result = indicator.calculate(sample_data)
    
    assert "ATR14" in result.columns
    
    # Calculate expected manually
    # TR for day 1: High(12) - Low(8) = 4 (prev_close is NaN, max is 4)
    # TR for day 2: High(13) - Low(9) = 4, High(13)-PrevClose(11)=2, Low(9)-PrevClose(11)=2 => TR=4
    # Day 1 ATR = 4
    # Day 2 ATR = Day 1 ATR + (alpha * (Day 2 TR - Day 1 ATR)) = 4 + (1/14)*(4-4) = 4
    assert result["ATR14"].iloc[0] == 4.0
    assert result["ATR14"].iloc[1] == 4.0


def test_atr20_calculation(sample_data):
    indicator = ATRIndicator(period=20)
    result = indicator.calculate(sample_data)
    
    assert "ATR20" in result.columns
    assert result["ATR20"].iloc[0] == 4.0


def test_original_dataframe_unchanged(sample_data):
    original_columns = list(sample_data.columns)
    
    indicator = ATRIndicator(period=14)
    indicator.calculate(sample_data)
    
    # Original should still have exactly the same columns
    assert list(sample_data.columns) == original_columns
    assert "ATR14" not in sample_data.columns


def test_missing_columns():
    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=2),
        "Close": [10.0, 11.0]
    })
    
    indicator = ATRIndicator()
    with pytest.raises(IndicatorValidationError, match="Missing required columns"):
        indicator.calculate(df)


def test_empty_dataframe():
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    
    indicator = ATRIndicator()
    with pytest.raises(IndicatorValidationError, match="cannot be empty"):
        indicator.calculate(df)


def test_output_properties(sample_data):
    indicator = ATRIndicator(period=14)
    result = indicator.calculate(sample_data)
    
    # Ensure row count is unchanged
    assert len(result) == len(sample_data)
    
    # Ensure ATR14 column exists
    assert "ATR14" in result.columns
