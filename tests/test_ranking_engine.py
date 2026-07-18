import pandas as pd
import pytest
import copy

from atlas.ranking.engine import RankingEngine, RankingError

@pytest.fixture
def sample_results():
    return [
        {
            "symbol": "RELIANCE",
            "institutional": True,
            "momentum": True,
            "vcp": False,
            "breakout": False,
        },
        {
            "symbol": "TCS",
            "institutional": False,
            "momentum": True,
            "vcp": True,
            "breakout": True,
        },
        {
            "symbol": "INFY",
            "institutional": True,
            "momentum": True,
            "vcp": True,
            "breakout": True,
        },
        {
            "symbol": "HDFCBANK",
            "institutional": False,
            "momentum": False,
            "vcp": False,
            "breakout": False,
        }
    ]

def test_normal_ranking(sample_results):
    engine = RankingEngine()
    df = engine.rank(sample_results)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4
    
    # INFY: 30 + 40 + 20 + 10 = 100
    # RELIANCE: 30 + 40 = 70
    # TCS: 40 + 20 + 10 = 70
    # HDFCBANK: 0
    
    # Expected order: INFY (100), RELIANCE (70), TCS (70), HDFCBANK (0)
    # Notice RELIANCE and TCS tie at 70. RELIANCE is alphabetically before TCS.
    
    assert df["Symbol"].iloc[0] == "INFY"
    assert df["Score"].iloc[0] == 100
    assert df["Rank"].iloc[0] == 1
    
    assert df["Symbol"].iloc[1] == "RELIANCE"
    assert df["Score"].iloc[1] == 70
    assert df["Rank"].iloc[1] == 2
    
    assert df["Symbol"].iloc[2] == "TCS"
    assert df["Score"].iloc[2] == 70
    assert df["Rank"].iloc[2] == 3
    
    assert df["Symbol"].iloc[3] == "HDFCBANK"
    assert df["Score"].iloc[3] == 0
    assert df["Rank"].iloc[3] == 4
    
    # Check shape/columns
    expected_cols = ["Rank", "Symbol", "Score", "Institutional", "Momentum", "VCP", "Breakout"]
    assert list(df.columns) == expected_cols


def test_tie_sorting():
    results = [
        {"symbol": "Z", "institutional": True, "momentum": False, "vcp": False, "breakout": False}, # 30
        {"symbol": "A", "institutional": True, "momentum": False, "vcp": False, "breakout": False}, # 30
    ]
    engine = RankingEngine()
    df = engine.rank(results)
    
    # Both score 30. "A" should be Rank 1, "Z" Rank 2.
    assert df["Symbol"].iloc[0] == "A"
    assert df["Symbol"].iloc[1] == "Z"


def test_configurable_weights():
    results = [
        {"symbol": "A", "custom1": True, "custom2": False},
        {"symbol": "B", "custom1": False, "custom2": True},
    ]
    
    weights = {"custom1": 10, "custom2": 90}
    engine = RankingEngine(weights=weights)
    df = engine.rank(results)
    
    # B scores 90, A scores 10
    assert df["Symbol"].iloc[0] == "B"
    assert df["Score"].iloc[0] == 90
    assert df["Symbol"].iloc[1] == "A"
    assert df["Score"].iloc[1] == 10
    
    # Custom1 should be capitalized to Custom1
    assert "Custom1" in df.columns
    assert "Custom2" in df.columns


def test_duplicate_symbols():
    results = [
        {"symbol": "A", "institutional": True, "momentum": False, "vcp": False, "breakout": False},
        {"symbol": "A", "institutional": True, "momentum": False, "vcp": False, "breakout": False},
    ]
    engine = RankingEngine()
    with pytest.raises(RankingError, match="Duplicate symbol"):
        engine.rank(results)


def test_missing_keys():
    results = [
        {"symbol": "A", "institutional": True, "momentum": False}, # Missing vcp, breakout
    ]
    engine = RankingEngine()
    with pytest.raises(RankingError, match="Missing required keys"):
        engine.rank(results)


def test_empty_input():
    engine = RankingEngine()
    with pytest.raises(RankingError, match="cannot be empty"):
        engine.rank([])


def test_input_unchanged(sample_results):
    original = copy.deepcopy(sample_results)
    engine = RankingEngine()
    engine.rank(sample_results)
    
    # The input list and dicts should not have any new keys like "Score" added
    assert sample_results == original
