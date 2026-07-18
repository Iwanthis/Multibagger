import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch

from atlas.providers.download_manager import DownloadManager, DownloadError

@pytest.fixture
def manager():
    return DownloadManager()

@pytest.fixture
def temp_data_dir(tmp_path):
    with patch("atlas.providers.download_manager.DAILY_DATA_DIR", tmp_path):
        yield tmp_path

@pytest.fixture
def mock_yf():
    with patch("atlas.providers.download_manager.yf.download") as mock:
        yield mock

def create_mock_df(empty=False, multi_index=True):
    if empty:
        return pd.DataFrame()
        
    data = {
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [102.0, 103.0],
        "Volume": [1000, 1100]
    }
    df = pd.DataFrame(data)
    df.index = pd.DatetimeIndex(["2023-01-01", "2023-01-02"], name="Date")
    
    if multi_index:
        df.columns = pd.MultiIndex.from_product([df.columns, ["RELIANCE.NS"]], names=["Price", "Ticker"])
        
    return df

def test_successful_download(manager, temp_data_dir, mock_yf):
    symbol = "RELIANCE"
    mock_yf.return_value = create_mock_df(multi_index=True)
    
    path = manager.download(symbol, period="1y")
    
    mock_yf.assert_called_once_with("RELIANCE.NS", period="1y", progress=False)
    assert path == temp_data_dir / "RELIANCE.csv"
    assert path.exists()
    
    saved_df = pd.read_csv(path)
    assert list(saved_df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert len(saved_df) == 2

def test_empty_dataframe(manager, temp_data_dir, mock_yf):
    symbol = "EMPTY"
    mock_yf.return_value = create_mock_df(empty=True)
    
    with pytest.raises(DownloadError, match="No data returned"):
        manager.download(symbol)

def test_download_failure(manager, temp_data_dir, mock_yf):
    symbol = "FAIL"
    mock_yf.side_effect = Exception("Network error")
    
    with pytest.raises(DownloadError, match="Download failed"):
        manager.download(symbol)

def test_multiple_downloads(manager, temp_data_dir, mock_yf):
    # RELIANCE works, FAIL returns empty dataframe (fails validation)
    def side_effect(symbol, *args, **kwargs):
        if "FAIL" in symbol:
            return create_mock_df(empty=True)
        return create_mock_df(multi_index=True)
        
    mock_yf.side_effect = side_effect
    
    results = manager.download_many(["RELIANCE", "FAIL"], period="1mo")
    
    assert results["RELIANCE"] is True
    assert results["FAIL"] is False
    assert (temp_data_dir / "RELIANCE.csv").exists()
    assert not (temp_data_dir / "FAIL.csv").exists()

def test_refresh(manager, temp_data_dir, mock_yf):
    symbol = "RELIANCE"
    mock_yf.return_value = create_mock_df(multi_index=True)
    
    # Touch file to simulate it exists
    path = temp_data_dir / f"{symbol}.csv"
    path.touch()
    
    returned_path = manager.refresh(symbol)
    
    assert returned_path == path
    mock_yf.assert_called_once_with("RELIANCE.NS", period="5y", progress=False)
    
    # Check if overwritten correctly
    saved_df = pd.read_csv(path)
    assert len(saved_df) == 2

def test_file_written_correctly(manager, temp_data_dir, mock_yf):
    symbol = "TCS"
    mock_yf.return_value = create_mock_df(multi_index=False)
    
    path = manager.download(symbol)
    saved_df = pd.read_csv(path)
    
    assert saved_df["Open"].iloc[0] == 100.0
    assert saved_df["Close"].iloc[1] == 103.0
    assert saved_df.shape == (2, 6)
