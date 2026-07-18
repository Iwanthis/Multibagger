import pandas as pd
import pytest

from atlas.scanners.base import Scanner, ScannerValidationError


class DummyScanner(Scanner):
    """A simple dummy scanner for testing the base class."""
    
    def scan(self, data: pd.DataFrame) -> pd.DataFrame:
        self._validate(data)
        return data.tail(1).copy()


def test_abstract_instantiation_fails():
    with pytest.raises(TypeError, match="Can't instantiate abstract class Scanner"):
        Scanner()


def test_empty_dataframe_validation():
    df = pd.DataFrame(columns=["Date", "Close"])
    scanner = DummyScanner()
    
    with pytest.raises(ScannerValidationError, match="cannot be empty"):
        scanner.scan(df)


class ValueScanner(Scanner):
    """A dummy scanner that matches rows where Close > 10.0"""
    def scan(self, data: pd.DataFrame) -> pd.DataFrame:
        self._validate(data)
        condition = data["Close"] > 10.0
        return data[condition].copy()

def test_scan_latest_with_latest_day_signal():
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Close": [5.0, 9.0, 11.0]
    })
    scanner = ValueScanner()
    # Historical scan should return 1 row
    assert len(scanner.scan(df)) == 1
    # Latest day is 11.0 > 10.0, so should be True
    assert scanner.scan_latest(df) is True

def test_scan_latest_with_historical_only_signal():
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Close": [11.0, 12.0, 9.0]
    })
    scanner = ValueScanner()
    # Historical scan should return 2 rows
    assert len(scanner.scan(df)) == 2
    # Latest day is 9.0 (fails), so should be False
    assert scanner.scan_latest(df) is False

def test_scan_latest_with_no_signal():
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Close": [5.0, 6.0, 7.0]
    })
    scanner = ValueScanner()
    assert len(scanner.scan(df)) == 0
    assert scanner.scan_latest(df) is False

def test_scan_latest_with_multiple_historical_signals():
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Close": [15.0, 16.0, 17.0]
    })
    scanner = ValueScanner()
    assert len(scanner.scan(df)) == 3
    assert scanner.scan_latest(df) is True
