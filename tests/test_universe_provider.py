import pandas as pd
import pytest
from unittest.mock import patch

from atlas.providers.universe_provider import UniverseProvider
from atlas.providers.market_data_provider import DataNotFoundError, DataValidationError

@pytest.fixture
def provider():
    return UniverseProvider()

@pytest.fixture
def temp_universe_dir(tmp_path):
    with patch("atlas.providers.universe_provider.UNIVERSE_DIR", tmp_path):
        yield tmp_path

def test_valid_universe(provider, temp_universe_dir):
    name = "valid"
    file_path = temp_universe_dir / f"{name}.csv"
    
    # Valid CSV with trailing spaces and blank rows
    content = "Symbol\nRELIANCE \n TCS\n\nINFY\n"
    file_path.write_text(content, encoding="utf-8")
    
    symbols = provider.get(name)
    assert symbols == ["RELIANCE", "TCS", "INFY"]

def test_missing_file(provider, temp_universe_dir):
    with pytest.raises(DataNotFoundError):
        provider.get("missing")

def test_missing_symbol_column(provider, temp_universe_dir):
    name = "invalid"
    file_path = temp_universe_dir / f"{name}.csv"
    
    # Missing 'Symbol' column
    df = pd.DataFrame({"Ticker": ["RELIANCE", "TCS"]})
    df.to_csv(file_path, index=False)
    
    with pytest.raises(DataValidationError, match="must contain a 'Symbol' column"):
        provider.get(name)

def test_duplicate_symbols(provider, temp_universe_dir):
    name = "duplicates"
    file_path = temp_universe_dir / f"{name}.csv"
    
    # Duplicates should be removed, order preserved
    content = "Symbol\nA\nB\nA\nC\nB\n"
    file_path.write_text(content, encoding="utf-8")
    
    symbols = provider.get(name)
    assert symbols == ["A", "B", "C"]

def test_blank_rows(provider, temp_universe_dir):
    name = "blanks"
    file_path = temp_universe_dir / f"{name}.csv"
    
    content = "Symbol\nA\n \nB\n\nC"
    file_path.write_text(content, encoding="utf-8")
    
    symbols = provider.get(name)
    assert symbols == ["A", "B", "C"]

def test_exists(provider, temp_universe_dir):
    name = "exists_test"
    file_path = temp_universe_dir / f"{name}.csv"
    
    assert not provider.exists(name)
    file_path.touch()
    assert provider.exists(name)

def test_list(provider, temp_universe_dir):
    (temp_universe_dir / "nifty50.csv").touch()
    (temp_universe_dir / "nifty500.csv").touch()
    
    universes = provider.list()
    assert universes == ["nifty50", "nifty500"]

def test_count(provider, temp_universe_dir):
    name = "count_test"
    file_path = temp_universe_dir / f"{name}.csv"
    
    content = "Symbol\nA\nB\nC\n"
    file_path.write_text(content, encoding="utf-8")
    
    assert provider.count(name) == 3
