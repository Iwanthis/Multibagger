import pytest
import pandas as pd
from pathlib import Path
from atlas.watchlists import WatchlistManager, WatchlistError

@pytest.fixture
def tmp_watchlists_dir(tmp_path):
    d = tmp_path / "watchlists"
    d.mkdir()
    return d

@pytest.fixture
def manager(tmp_watchlists_dir):
    return WatchlistManager(watchlists_dir=tmp_watchlists_dir)

def test_watchlist_creation(manager):
    manager.create("momentum")
    assert manager.exists("momentum")
    assert "momentum" in manager.list()
    
    # Check that it has headers DateAdded and Symbol
    df = manager.load("momentum")
    assert list(df.columns) == ["DateAdded", "Symbol"]
    assert df.empty
    
    # Creation of duplicate throws error
    with pytest.raises(WatchlistError, match="already exists"):
        manager.create("momentum")

def test_add_symbol_and_duplicate_prevention(manager):
    manager.create("vcp")
    manager.add("vcp", "FEDERALBNK")
    
    df = manager.load("vcp")
    assert len(df) == 1
    assert df.iloc[0]["Symbol"] == "FEDERALBNK"
    assert "DateAdded" in df.columns
    
    # Adding duplicate should be a no-op
    manager.add("vcp", "federalbnk")
    df_after = manager.load("vcp")
    assert len(df_after) == 1

def test_remove_symbol_and_missing(manager):
    manager.create("manual")
    manager.add("manual", "TCS")
    manager.add("manual", "INFY")
    
    assert manager.contains("manual", "TCS")
    
    manager.remove("manual", "TCS")
    assert not manager.contains("manual", "TCS")
    
    df = manager.load("manual")
    assert len(df) == 1
    
    # Removing missing should not raise
    manager.remove("manual", "RELIANCE")

def test_alphabetical_ordering(manager):
    manager.create("alpha")
    manager.add("alpha", "ZOMATO")
    manager.add("alpha", "APPLE")
    manager.add("alpha", "MICROSOFT")
    
    df = manager.load("alpha")
    symbols = df["Symbol"].tolist()
    assert symbols == ["APPLE", "MICROSOFT", "ZOMATO"]

def test_multiple_watchlists(manager):
    manager.create("list1")
    manager.create("list2")
    manager.create("list3")
    
    manager.add("list1", "A")
    manager.add("list2", "B")
    
    assert manager.list() == ["list1", "list2", "list3"]
    assert manager.contains("list1", "A")
    assert not manager.contains("list2", "A")

def test_dataframe_immutability(manager):
    manager.create("immutable")
    df = pd.DataFrame({"DateAdded": ["2023-01-01"], "Symbol": ["Z"]})
    original = df.copy(deep=True)
    
    manager.save("immutable", df)
    pd.testing.assert_frame_equal(df, original)

def test_nonexistent_watchlist_load(manager):
    with pytest.raises(WatchlistError, match="does not exist"):
        manager.load("ghost")

def test_add_to_nonexistent(manager):
    with pytest.raises(WatchlistError, match="does not exist"):
        manager.add("ghost", "AAPL")
