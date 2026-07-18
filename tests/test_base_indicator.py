import pandas as pd
import pytest

from atlas.indicators.base import Indicator, IndicatorValidationError

class DummyIndicator(Indicator):
    """A simple dummy indicator for testing the base class."""
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        self._validate_dataframe(data)
        data = data.copy()
        data["Dummy"] = data["Close"] * 2
        return data

def test_abstract_instantiation_fails():
    with pytest.raises(TypeError, match="Can't instantiate abstract class Indicator"):
        Indicator()

def test_valid_dataframe():
    df = pd.DataFrame({
        "Date": ["2023-01-01"],
        "Open": [10.0],
        "High": [12.0],
        "Low": [9.0],
        "Close": [11.0],
        "Volume": [1000]
    })
    
    indicator = DummyIndicator()
    # Should not raise exception
    result = indicator.calculate(df)
    
    assert "Dummy" in result.columns
    assert result["Dummy"].iloc[0] == 22.0

def test_missing_columns():
    df = pd.DataFrame({
        "Date": ["2023-01-01"],
        "Open": [10.0],
        "Close": [11.0]
        # Missing High, Low, Volume
    })
    
    indicator = DummyIndicator()
    with pytest.raises(IndicatorValidationError, match="Missing required columns"):
        indicator.calculate(df)

def test_empty_dataframe():
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    
    indicator = DummyIndicator()
    with pytest.raises(IndicatorValidationError, match="cannot be empty"):
        indicator.calculate(df)
