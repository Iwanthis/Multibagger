
import pytest
import pandas as pd
from unittest.mock import patch
from typer.testing import CliRunner

from atlas.cli.commands import app
from atlas.config import settings

runner = CliRunner()

@pytest.fixture
def temp_data_env(tmp_path):
    """Sets up a temporary real filesystem environment for integration testing."""
    universe_dir = tmp_path / "universe"
    daily_dir = tmp_path / "daily"
    universe_dir.mkdir()
    daily_dir.mkdir()
    
    # Create a universe file
    uni_path = universe_dir / "my_test.csv"
    pd.DataFrame({"Symbol": ["A", "B", "C", "D", "E"]}).to_csv(uni_path, index=False)
    
    # Create valid market data for 'A' (The perfect stock)
    dates = pd.date_range("2020-01-01", periods=300)
    df_a = pd.DataFrame({
        "Date": dates,
        "Open": [100.0] * 300,
        "High": [105.0] * 300,
        "Low": [95.0] * 300,
        "Close": [102.0] * 300,
        "Volume": [10000] * 300
    })
    df_a.to_csv(daily_dir / "A.csv", index=False)
    
    # Create benchmark data for Relative Strength
    df_a.to_csv(daily_dir / "^NSEI.csv", index=False)
    
    # Create market data for 'B' (missing volume column - invalid)
    df_b = df_a.drop(columns=["Volume"])
    df_b.to_csv(daily_dir / "B.csv", index=False)
    
    # 'C' is missing completely (tests missing CSV DataNotFoundError)
    
    # 'D' is empty dataframe
    pd.DataFrame(columns=df_a.columns).to_csv(daily_dir / "D.csv", index=False)
    
    # 'E' valid data but flat (fails scanners)
    df_e = df_a.copy()
    df_e["Close"] = 10.0 # Will fail EMAs
    df_e.to_csv(daily_dir / "E.csv", index=False)
    
    # Patch module-level imported constants
    with patch("atlas.providers.universe_provider.UNIVERSE_DIR", universe_dir), \
         patch("atlas.providers.market_data_provider.DAILY_DATA_DIR", daily_dir), \
         patch("atlas.cli.commands.settings.UNIVERSE_DIR", universe_dir), \
         patch("atlas.cli.commands.settings.DAILY_DATA_DIR", daily_dir):
        yield


def test_end_to_end_pipeline(temp_data_env):
    """
    Integration test validating:
    - pipeline completes
    - report generated
    - ranking produced
    - failures handled gracefully (missing CSV, invalid data)
    """
    result = runner.invoke(app, ["scan", "my_test"])
    
    assert result.exit_code == 0
    assert "Scan failed" not in result.stdout
    assert "MULTIBAGGER DAILY REPORT" in result.stdout
    
    # 5 total in universe, B (invalid), C (missing), D (empty) fail data loading safely
    # So 2 (A and E) are scanned successfully through the entire pipeline
    assert "Stocks Scanned: 2" in result.stdout
    assert "Rank" in result.stdout


def test_empty_universe(temp_data_env, tmp_path):
    """Integration test validating empty universe handling."""
    pd.DataFrame(columns=["Symbol"]).to_csv(tmp_path / "universe" / "empty.csv", index=False)
    
    result = runner.invoke(app, ["scan", "empty"])
    assert result.exit_code == 0
    assert "No stocks successfully scanned." in result.stdout


@patch("atlas.cli.commands.DownloadManager")
def test_download_mocked(mock_manager, temp_data_env):
    """Validates that download orchestration integrates with the provider."""
    result = runner.invoke(app, ["download", "my_test"])
    assert result.exit_code == 0
    mock_manager.return_value.download_many.assert_called_once_with(["A", "B", "C", "D", "E"])
