import pandas as pd
import pytest

from atlas.scanners.momentum import MomentumScanner
from atlas.scanners.base import ScannerValidationError


@pytest.fixture
def base_data():
    """Provides a deterministic starting point for momentum scanner tests."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=3),
        "Close": [90.0, 95.0, 100.0],
        "EMA20": [85.0, 90.0, 95.0],
        "EMA50": [80.0, 85.0, 90.0],
        "EMA200": [75.0, 80.0, 85.0],
        "HIGH252": [100.0, 100.0, 102.0],
        "RVOL20": [1.0, 1.0, 1.5],
        "MomentumScore": [50.0, 60.0, 80.0],
        "Volume": [1000] * 3
    })
    # Default rules: score >= 70, rvol >= 1.20, close >= high * 0.95
    # Row 0, 1: Would fail rules, but scanner ONLY evaluates Row 2.
    # Row 2 (Latest):
    # Trend: 100 > 95 > 90 > 85 (Pass)
    # RVOL: 1.5 >= 1.20 (Pass)
    # HIGH: 100 >= 102 * 0.95 (100 >= 96.9) (Pass)
    # Score: 80 >= 70 (Pass)
    # Result: Passes!


def test_perfect_momentum_stock(base_data):
    scanner = MomentumScanner()
    result = scanner.scan(base_data)
    
    assert len(result) == 1
    assert result.index[0] == 2
    assert result["Date"].iloc[0] == pd.Timestamp("2023-01-03")


def test_historic_signal_ignored(base_data):
    # If the latest day fails, but day 1 was perfect, it should still return empty.
    df = base_data.copy()
    # Ruin day 2's trend
    df.loc[2, "Close"] = 80.0 
    # Make day 1 perfect
    df.loc[1, "RVOL20"] = 2.0
    df.loc[1, "MomentumScore"] = 90.0
    
    scanner = MomentumScanner()
    result = scanner.scan(df)
    
    assert len(result) == 0


def test_below_ema20(base_data):
    df = base_data.copy()
    df.loc[2, "Close"] = 94.0 # Less than EMA20 (95.0)
    
    scanner = MomentumScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_ema_alignment_failure(base_data):
    df = base_data.copy()
    df.loc[2, "EMA50"] = 96.0 # EMA50 > EMA20 (95.0)
    
    scanner = MomentumScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_low_rvol(base_data):
    df = base_data.copy()
    df.loc[2, "RVOL20"] = 1.19
    
    scanner = MomentumScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_low_momentum_score(base_data):
    df = base_data.copy()
    df.loc[2, "MomentumScore"] = 69.9
    
    scanner = MomentumScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_not_near_high(base_data):
    df = base_data.copy()
    df.loc[2, "HIGH252"] = 120.0 # 120 * 0.95 = 114. Close 100 < 114.
    
    scanner = MomentumScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_parameter_override(base_data):
    df = base_data.copy()
    df.loc[2, "MomentumScore"] = 50.0 # Will fail default 70
    
    scanner_fail = MomentumScanner()
    assert len(scanner_fail.scan(df)) == 0
    
    # Override
    scanner_pass = MomentumScanner(minimum_score=40.0)
    assert len(scanner_pass.scan(df)) == 1


def test_missing_required_columns(base_data):
    df = base_data.drop(columns=["MomentumScore"])
    
    scanner = MomentumScanner()
    with pytest.raises(ScannerValidationError, match="Missing required columns"):
        scanner.scan(df)


def test_empty_dataframe(base_data):
    df = pd.DataFrame(columns=base_data.columns)
    
    scanner = MomentumScanner()
    with pytest.raises(ScannerValidationError, match="cannot be empty"):
        scanner.scan(df)


def test_original_dataframe_unchanged(base_data):
    original_columns = list(base_data.columns)
    original_len = len(base_data)
    
    scanner = MomentumScanner()
    scanner.scan(base_data)
    
    assert list(base_data.columns) == original_columns
    assert len(base_data) == original_len
