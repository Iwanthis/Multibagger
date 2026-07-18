import pandas as pd
import pytest
import numpy as np

from atlas.indicators.relative_volume import RelativeVolumeIndicator
from atlas.indicators.base import IndicatorValidationError


@pytest.fixture
def sample_data():
    """Provides deterministic sample data for testing."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=10),
        "Open": [10.0] * 10,
        "High": [12.0] * 10,
        "Low": [8.0] * 10,
        "Close": [11.0] * 10,
        # Constant volume except the last 2 days
        "Volume": [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 2000, 500]
    })


def test_rvol3_calculation(sample_data):
    # Using a period of 3 for shorter testing against sample_data
    indicator = RelativeVolumeIndicator(period=3)
    result = indicator.calculate(sample_data)
    
    assert "RVOL3" in result.columns
    
    # Day 0, 1 should be NaN
    assert pd.isna(result["RVOL3"].iloc[0])
    assert pd.isna(result["RVOL3"].iloc[1])
    
    # Day 2: Avg(1000, 1000, 1000) = 1000. RVOL = 1000/1000 = 1.0
    assert result["RVOL3"].iloc[2] == 1.0
    
    # Day 8: Vol=2000. Prev vols: Day 6=1000, Day 7=1000. Avg = (1000+1000+2000)/3 = 1333.333
    # RVOL = 2000 / 1333.333 = 1.5
    expected_rvol8 = 2000 / ((1000 + 1000 + 2000) / 3)
    assert result["RVOL3"].iloc[8] == pytest.approx(expected_rvol8)


def test_rvol20_calculation():
    # To test RVOL20 we need at least 20 rows
    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=25),
        "Open": [10.0] * 25,
        "High": [12.0] * 25,
        "Low": [8.0] * 25,
        "Close": [11.0] * 25,
        "Volume": [1000] * 24 + [2000] # Constant 1000 for 24 days, 2000 on 25th day
    })
    
    indicator = RelativeVolumeIndicator(period=20)
    result = indicator.calculate(df)
    
    assert "RVOL20" in result.columns
    
    # Index 18 should be NaN (19th day)
    assert pd.isna(result["RVOL20"].iloc[18])
    
    # Index 19 is the 20th day. Vol=1000, Avg=1000, RVOL=1.0
    assert result["RVOL20"].iloc[19] == 1.0
    
    # Index 24 is the 25th day. Vol=2000. Avg of last 20 days: 19 days of 1000, 1 day of 2000
    # sum = 19000 + 2000 = 21000. avg = 21000 / 20 = 1050
    # RVOL = 2000 / 1050 = 1.90476...
    assert result["RVOL20"].iloc[24] == pytest.approx(2000 / 1050)


def test_original_dataframe_unchanged(sample_data):
    original_columns = list(sample_data.columns)
    
    indicator = RelativeVolumeIndicator(period=3)
    indicator.calculate(sample_data)
    
    # Original should still have exactly the same columns
    assert list(sample_data.columns) == original_columns
    assert "RVOL3" not in sample_data.columns


def test_missing_columns():
    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=2),
        "Close": [10.0, 11.0]
    })
    
    indicator = RelativeVolumeIndicator()
    with pytest.raises(IndicatorValidationError, match="Missing required columns"):
        indicator.calculate(df)


def test_empty_dataframe():
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    
    indicator = RelativeVolumeIndicator()
    with pytest.raises(IndicatorValidationError, match="cannot be empty"):
        indicator.calculate(df)


def test_output_properties(sample_data):
    indicator = RelativeVolumeIndicator(period=3)
    result = indicator.calculate(sample_data)
    
    # Ensure row count is unchanged
    assert len(result) == len(sample_data)
    
    # Ensure RVOL3 column exists
    assert "RVOL3" in result.columns
