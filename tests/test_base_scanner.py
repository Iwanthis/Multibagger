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


def test_dummy_scanner_returns_dataframe():
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Close": [10.0, 11.0, 12.0]
    })
    
    scanner = DummyScanner()
    result = scanner.scan(df)
    
    assert isinstance(result, pd.DataFrame)
    
    
def test_dummy_scanner_correct_row_count():
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Close": [10.0, 11.0, 12.0]
    })
    
    scanner = DummyScanner()
    result = scanner.scan(df)
    
    # Should only return the last row (tail(1))
    assert len(result) == 1
    assert result["Close"].iloc[0] == 12.0
    assert result["Date"].iloc[0] == "2023-01-03"
