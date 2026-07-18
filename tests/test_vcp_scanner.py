import pandas as pd
import pytest

from atlas.scanners.vcp import VCPScanner
from atlas.scanners.base import ScannerValidationError


@pytest.fixture
def base_data():
    """Provides a deterministic starting point for VCP scanner tests."""
    # We need at least lookback + 1 rows to test ATR contraction properly.
    # By default lookback is 10, so we need 11 rows.
    # Let's provide 12 rows.
    # The previous 10 rows before the last row will have ATR14 = 10.0
    # Average ATR = 10.0
    # The last row will have ATR14 = 7.0
    # 7.0 <= 10.0 * 0.80 (8.0). So ATR contraction passes.
    
    dates = pd.date_range(start="2023-01-01", periods=12)
    atr = [10.0] * 11 + [7.0]
    
    # Latest row requirements:
    # Trend: EMA20 > EMA50 > EMA200 (95 > 90 > 85), Close > EMA20 (100 > 95)
    # Near high: Close(100) >= High252(102) * 0.95 (96.9)
    # RVOL: 1.5 >= 1.20
    
    return pd.DataFrame({
        "Date": dates,
        "Close": [90.0] * 11 + [100.0],
        "High": [95.0] * 11 + [102.0],
        "Low": [85.0] * 11 + [98.0],
        "ATR14": atr,
        "RVOL20": [1.0] * 11 + [1.5],
        "HIGH252": [102.0] * 12,
        "EMA20": [80.0] * 11 + [95.0],
        "EMA50": [75.0] * 11 + [90.0],
        "EMA200": [70.0] * 11 + [85.0],
    })


def test_perfect_vcp(base_data):
    scanner = VCPScanner()
    result = scanner.scan(base_data)
    
    assert len(result) == 1
    assert result.index[0] == 11
    assert result["Date"].iloc[0] == pd.Timestamp("2023-01-12")


def test_atr_not_contracted(base_data):
    df = base_data.copy()
    # 8.1 is > 10.0 * 0.80, so it should fail
    df.loc[11, "ATR14"] = 8.1 
    
    scanner = VCPScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_low_rvol(base_data):
    df = base_data.copy()
    df.loc[11, "RVOL20"] = 1.19
    
    scanner = VCPScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_not_near_high(base_data):
    df = base_data.copy()
    df.loc[11, "HIGH252"] = 120.0
    
    scanner = VCPScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_ema_alignment_failure(base_data):
    df = base_data.copy()
    df.loc[11, "EMA200"] = 92.0 # Breaks EMA50 > EMA200
    
    scanner = VCPScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_insufficient_history(base_data):
    # Pass only 5 rows, but lookback is 10.
    df = base_data.tail(5).copy()
    
    scanner = VCPScanner()
    result = scanner.scan(df)
    assert len(result) == 0


def test_parameter_override(base_data):
    df = base_data.copy()
    # Fails default 0.80 contraction
    df.loc[11, "ATR14"] = 8.5 
    
    scanner_fail = VCPScanner()
    assert len(scanner_fail.scan(df)) == 0
    
    # Override contraction requirement to 0.90
    scanner_pass = VCPScanner(atr_contraction=0.90)
    assert len(scanner_pass.scan(df)) == 1


def test_missing_required_columns(base_data):
    df = base_data.drop(columns=["ATR14"])
    
    scanner = VCPScanner()
    with pytest.raises(ScannerValidationError, match="Missing required columns"):
        scanner.scan(df)


def test_empty_dataframe(base_data):
    df = pd.DataFrame(columns=base_data.columns)
    
    scanner = VCPScanner()
    with pytest.raises(ScannerValidationError, match="cannot be empty"):
        scanner.scan(df)


def test_original_dataframe_unchanged(base_data):
    original_columns = list(base_data.columns)
    original_len = len(base_data)
    
    scanner = VCPScanner()
    scanner.scan(base_data)
    
    assert list(base_data.columns) == original_columns
    assert len(base_data) == original_len
