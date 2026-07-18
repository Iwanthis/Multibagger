import pandas as pd
import pytest

from atlas.scanners.institutional import InstitutionalScanner
from atlas.scanners.base import ScannerValidationError


@pytest.fixture
def base_data():
    """Provides a deterministic starting point for scanner tests."""
    return pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=6),
        "Open": [100.0, 100.0, 100.0, 100.0, 105.0, 100.0],
        "High": [110.0, 110.0, 110.0, 110.0, 110.0, 110.0],
        "Low": [98.0, 98.0, 98.0, 98.0, 98.0, 98.0],
        "Close": [108.0, 108.0, 103.0, 108.0, 100.0, 108.0],
        "ATR14": [5.0, 5.0, 5.0, 20.0, 5.0, 5.0],
        "RVOL20": [3.0, 1.0, 3.0, 3.0, 3.0, 3.0],
        "OtherCol": [1, 2, 3, 4, 5, 6]
    })
    
    # Let's break down the rules for default parameters:
    # rvol_threshold = 2.0
    # body_threshold = 0.60
    # atr_multiplier = 1.0
    
    # Range is always High - Low = 110 - 98 = 12.0
    
    # Row 0: Perfect institutional candle
    # Open: 100, Close: 108 => Bullish
    # Body = 8.0. Body % = 8.0 / 12.0 = 0.666 (Strong Body pass > 0.60)
    # Range = 12.0. ATR = 5.0 * 1.0 = 5.0. 12.0 > 5.0 (ATR pass)
    # RVOL = 3.0 (RVOL pass >= 2.0)
    
    # Row 1: Low RVOL
    # Same as Row 0, but RVOL = 1.0 (Fail)
    
    # Row 2: Weak candle body
    # Close = 103, Body = 3. Body % = 3 / 12 = 0.25 (Fail)
    
    # Row 3: ATR too small (Range not > ATR * multiplier)
    # ATR = 20.0. Range 12.0 is NOT > 20.0 (Fail)
    
    # Row 4: Bearish candle
    # Open = 105, Close = 100 (Fail, not bullish)
    
    # Row 5: Another perfect candle to ensure multiple returns work
    # Identical to Row 0.


def test_scanner_logic(base_data):
    scanner = InstitutionalScanner()
    result = scanner.scan(base_data)
    
    # Should only return rows 0 and 5
    assert len(result) == 2
    assert result.index.tolist() == [0, 5]
    

def test_missing_required_columns(base_data):
    # Drop required column 'ATR14'
    df = base_data.drop(columns=["ATR14"])
    
    scanner = InstitutionalScanner()
    with pytest.raises(ScannerValidationError, match="Missing required columns"):
        scanner.scan(df)
        

def test_empty_dataframe(base_data):
    df = pd.DataFrame(columns=base_data.columns)
    
    scanner = InstitutionalScanner()
    with pytest.raises(ScannerValidationError, match="cannot be empty"):
        scanner.scan(df)
        

def test_parameter_override():
    # If we lower the body_threshold to 0.20, then Row 2 (body % = 0.25) should pass
    df = pd.DataFrame({
        "Date": ["2023-01-01"],
        "Open": [100.0],
        "High": [110.0],
        "Low": [98.0],
        "Close": [103.0], # Body = 3, % = 0.25
        "ATR14": [5.0],
        "RVOL20": [3.0]
    })
    
    # Default fails
    scanner_default = InstitutionalScanner()
    res1 = scanner_default.scan(df)
    assert len(res1) == 0
    
    # Override passes
    scanner_override = InstitutionalScanner(body_threshold=0.20)
    res2 = scanner_override.scan(df)
    assert len(res2) == 1


def test_original_dataframe_unchanged(base_data):
    original_columns = list(base_data.columns)
    original_len = len(base_data)
    
    scanner = InstitutionalScanner()
    scanner.scan(base_data)
    
    assert list(base_data.columns) == original_columns
    assert len(base_data) == original_len
