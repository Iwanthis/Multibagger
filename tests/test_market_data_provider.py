import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch

from atlas.providers.market_data_provider import (
    MarketDataProvider, 
    DataNotFoundError, 
    DataValidationError
)

@pytest.fixture
def provider():
    return MarketDataProvider()

@pytest.fixture
def temp_data_dir(tmp_path):
    # Mock the DAILY_DATA_DIR to point to our temp directory for tests
    with patch("atlas.providers.market_data_provider.DAILY_DATA_DIR", tmp_path):
        yield tmp_path

def test_valid_file(provider, temp_data_dir):
    symbol = "VALID"
    file_path = temp_data_dir / f"{symbol}.csv"
    
    # Create valid CSV
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Open": [100.0, 101.0, 102.0],
        "High": [105.0, 106.0, 107.0],
        "Low": [95.0, 96.0, 97.0],
        "Close": [102.0, 103.0, 104.0],
        "Volume": [1000, 1100, 1200]
    })
    df.to_csv(file_path, index=False)
    
    result = provider.get(symbol)
    assert not result.empty
    assert len(result) == 3
    assert result["Date"].dtype == "datetime64[ns]"
    assert result["Close"].iloc[-1] == 104.0

def test_missing_file(provider, temp_data_dir):
    with pytest.raises(DataNotFoundError):
        provider.get("MISSING")

def test_invalid_columns(provider, temp_data_dir):
    symbol = "INVALID_COLS"
    file_path = temp_data_dir / f"{symbol}.csv"
    
    # Missing 'Volume'
    df = pd.DataFrame({
        "Date": ["2023-01-01"],
        "Open": [100.0],
        "High": [105.0],
        "Low": [95.0],
        "Close": [102.0]
    })
    df.to_csv(file_path, index=False)
    
    with pytest.raises(DataValidationError, match="Missing required columns"):
        provider.get(symbol)

def test_duplicate_dates(provider, temp_data_dir):
    symbol = "DUPLICATE"
    file_path = temp_data_dir / f"{symbol}.csv"
    
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-01", "2023-01-02"],
        "Open": [100.0, 101.0, 102.0],
        "High": [105.0, 106.0, 107.0],
        "Low": [95.0, 96.0, 97.0],
        "Close": [102.0, 103.0, 104.0],
        "Volume": [1000, 1100, 1200]
    })
    df.to_csv(file_path, index=False)
    
    result = provider.get(symbol)
    assert len(result) == 2  # one duplicate removed
    # Last duplicate is kept in our logic
    assert result["Close"].iloc[0] == 103.0

def test_empty_dataframe(provider, temp_data_dir):
    symbol = "EMPTY"
    file_path = temp_data_dir / f"{symbol}.csv"
    
    df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    df.to_csv(file_path, index=False)
    
    with pytest.raises(DataValidationError, match="is empty"):
        provider.get(symbol)

def test_exists(provider, temp_data_dir):
    symbol = "EXISTS"
    file_path = temp_data_dir / f"{symbol}.csv"
    
    assert not provider.exists(symbol)
    
    file_path.touch()
    
    assert provider.exists(symbol)

def test_list_symbols(provider, temp_data_dir):
    (temp_data_dir / "AAA.csv").touch()
    (temp_data_dir / "BBB.csv").touch()
    
    symbols = provider.list_symbols()
    assert symbols == ["AAA", "BBB"]

def test_latest(provider, temp_data_dir):
    symbol = "LATEST"
    file_path = temp_data_dir / f"{symbol}.csv"
    
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02"],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [102.0, 103.0],
        "Volume": [1000, 1100]
    })
    df.to_csv(file_path, index=False)
    
    latest_row = provider.latest(symbol)
    assert latest_row["Close"] == 103.0
    assert str(latest_row["Date"].date()) == "2023-01-02"
