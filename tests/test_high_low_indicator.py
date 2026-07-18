import pandas as pd
import pytest

from atlas.indicators.high_low import HighLowIndicator
from atlas.indicators.base import IndicatorValidationError


@pytest.fixture
def sample_data():
    """Provides deterministic sample data for testing."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=10),
        "Open": [10.0] * 10,
        "High": [12.0, 13.0, 15.0, 14.0, 16.0, 15.0, 18.0, 17.0, 19.0, 16.0],
        "Low":  [8.0, 9.0, 7.0, 8.0, 6.0, 7.0, 9.0, 5.0, 8.0, 6.0],
        "Close": [11.0] * 10,
        "Volume": [1000] * 10
    })


def test_high_low_3_calculation(sample_data):
    # Use a period of 3 for shorter testing against sample_data
    indicator = HighLowIndicator(period=3)
    result = indicator.calculate(sample_data)
    
    assert "HIGH3" in result.columns
    assert "LOW3" in result.columns
    
    # Day 0, 1 should be NaN
    assert pd.isna(result["HIGH3"].iloc[0])
    assert pd.isna(result["LOW3"].iloc[1])
    
    # Day 2: Highs are [12.0, 13.0, 15.0]. Max = 15.0
    # Day 2: Lows are [8.0, 9.0, 7.0]. Min = 7.0
    assert result["HIGH3"].iloc[2] == 15.0
    assert result["LOW3"].iloc[2] == 7.0
    
    # Day 7: Highs are [15.0, 18.0, 17.0]. Max = 18.0
    # Day 7: Lows are [7.0, 9.0, 5.0]. Min = 5.0
    assert result["HIGH3"].iloc[7] == 18.0
    assert result["LOW3"].iloc[7] == 5.0


def test_high_low_252_calculation():
    # To test HIGH252 we need at least 252 rows
    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=260),
        "Open": [10.0] * 260,
        "High": [15.0] * 251 + [25.0] + [20.0] * 8, # Max hits exactly on index 251
        "Low": [10.0] * 251 + [5.0] + [8.0] * 8,    # Min hits exactly on index 251
        "Close": [11.0] * 260,
        "Volume": [1000] * 260
    })
    
    indicator = HighLowIndicator(period=252)
    result = indicator.calculate(df)
    
    assert "HIGH252" in result.columns
    assert "LOW252" in result.columns
    
    # Index 250 should be NaN (251st day)
    assert pd.isna(result["HIGH252"].iloc[250])
    assert pd.isna(result["LOW252"].iloc[250])
    
    # Index 251 is the 252nd day. Max High = 25.0, Min Low = 5.0
    assert result["HIGH252"].iloc[251] == 25.0
    assert result["LOW252"].iloc[251] == 5.0


def test_original_dataframe_unchanged(sample_data):
    original_columns = list(sample_data.columns)
    
    indicator = HighLowIndicator(period=3)
    indicator.calculate(sample_data)
    
    assert list(sample_data.columns) == original_columns
    assert "HIGH3" not in sample_data.columns
    assert "LOW3" not in sample_data.columns


def test_missing_columns():
    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=2),
        "Close": [10.0, 11.0]
    })
    
    indicator = HighLowIndicator()
    with pytest.raises(IndicatorValidationError, match="Missing required columns"):
        indicator.calculate(df)


def test_empty_dataframe():
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    
    indicator = HighLowIndicator()
    with pytest.raises(IndicatorValidationError, match="cannot be empty"):
        indicator.calculate(df)


def test_output_properties(sample_data):
    indicator = HighLowIndicator(period=3)
    result = indicator.calculate(sample_data)
    
    # Ensure row count is unchanged
    assert len(result) == len(sample_data)
