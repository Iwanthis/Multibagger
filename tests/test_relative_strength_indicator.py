import pandas as pd
import pytest

from atlas.indicators.relative_strength import RelativeStrengthIndicator
from atlas.indicators.base import IndicatorValidationError


@pytest.fixture
def stock_data():
    """Provides deterministic sample stock data for testing."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=10),
        "Open": [10.0] * 10,
        "High": [12.0] * 10,
        "Low": [8.0] * 10,
        "Close": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 20.0],
        "Volume": [1000] * 10
    })


@pytest.fixture
def benchmark_data():
    """Provides deterministic sample benchmark data for testing."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=10),
        "Open": [100.0] * 10,
        "High": [120.0] * 10,
        "Low": [80.0] * 10,
        "Close": [100.0, 102.0, 104.0, 106.0, 108.0, 110.0, 112.0, 114.0, 116.0, 118.0],
        "Volume": [5000] * 10
    })


def test_rs2_calculation(stock_data, benchmark_data):
    # Using period 2 for testing
    indicator = RelativeStrengthIndicator(period=2)
    result = indicator.calculate(stock_data, benchmark_data)
    
    assert "RS2" in result.columns
    
    # Day 0, 1 should be NaN
    assert pd.isna(result["RS2"].iloc[0])
    assert pd.isna(result["RS2"].iloc[1])
    
    # Day 2:
    # Stock Close: Day 0=10.0, Day 2=12.0 -> Return = 12/10 - 1 = 0.2
    # Bench Close: Day 0=100.0, Day 2=104.0 -> Return = 104/100 - 1 = 0.04
    # RS2 = 0.2 - 0.04 = 0.16
    assert result["RS2"].iloc[2] == pytest.approx(0.16)
    
    # Day 9:
    # Stock Close: Day 7=17.0, Day 9=20.0 -> Return = 20/17 - 1 = 0.1764705
    # Bench Close: Day 7=114.0, Day 9=118.0 -> Return = 118/114 - 1 = 0.0350877
    # RS2 = 0.1764705 - 0.0350877 = 0.1413828
    expected_rs9 = (20.0 / 17.0 - 1) - (118.0 / 114.0 - 1)
    assert result["RS2"].iloc[9] == pytest.approx(expected_rs9)


def test_original_dataframe_unchanged(stock_data, benchmark_data):
    original_stock_columns = list(stock_data.columns)
    original_bench_columns = list(benchmark_data.columns)
    
    indicator = RelativeStrengthIndicator(period=2)
    indicator.calculate(stock_data, benchmark_data)
    
    assert list(stock_data.columns) == original_stock_columns
    assert "RS2" not in stock_data.columns
    assert list(benchmark_data.columns) == original_bench_columns


def test_unequal_dataframe_lengths(stock_data, benchmark_data):
    # Drop one row from benchmark
    short_benchmark = benchmark_data.drop(9)
    
    indicator = RelativeStrengthIndicator(period=2)
    with pytest.raises(IndicatorValidationError, match="equal length"):
        indicator.calculate(stock_data, short_benchmark)


def test_mismatched_dates(stock_data, benchmark_data):
    # Change one date in benchmark
    mismatched_benchmark = benchmark_data.copy()
    mismatched_benchmark.loc[5, "Date"] = pd.Timestamp("2024-01-01")
    
    indicator = RelativeStrengthIndicator(period=2)
    with pytest.raises(IndicatorValidationError, match="align by Date"):
        indicator.calculate(stock_data, mismatched_benchmark)


def test_missing_columns(benchmark_data):
    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=10),
        "Close": [10.0] * 10
    })
    
    indicator = RelativeStrengthIndicator()
    with pytest.raises(IndicatorValidationError, match="Missing required columns"):
        indicator.calculate(df, benchmark_data)


def test_empty_dataframe(benchmark_data):
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    
    indicator = RelativeStrengthIndicator()
    with pytest.raises(IndicatorValidationError, match="cannot be empty"):
        indicator.calculate(df, benchmark_data)


def test_output_properties(stock_data, benchmark_data):
    indicator = RelativeStrengthIndicator(period=2)
    result = indicator.calculate(stock_data, benchmark_data)
    
    # Ensure row count is unchanged
    assert len(result) == len(stock_data)
