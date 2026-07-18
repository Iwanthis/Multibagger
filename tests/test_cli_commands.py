import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from atlas.cli.commands import app

runner = CliRunner()

def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Multibagger" in result.stdout
    assert "Atlas Framework" in result.stdout
    assert "Version" in result.stdout


@patch("atlas.cli.commands.UniverseProvider")
def test_list_universes(mock_provider):
    instance = mock_provider.return_value
    instance.list.return_value = ["nifty50", "nifty500"]
    
    result = runner.invoke(app, ["list-universes"])
    assert result.exit_code == 0
    assert "nifty500" in result.stdout
    assert "nifty50" in result.stdout


@patch("atlas.cli.commands.UniverseProvider")
def test_missing_universe(mock_provider):
    instance = mock_provider.return_value
    instance.get.side_effect = Exception("Universe not found")
    
    result = runner.invoke(app, ["download", "missing"])
    assert result.exit_code == 0
    assert "Error: Universe not found" in result.stdout


@patch("atlas.cli.commands.UniverseProvider")
@patch("atlas.cli.commands.DownloadManager")
def test_download_command(mock_manager, mock_provider):
    provider_instance = mock_provider.return_value
    provider_instance.get.return_value = ["RELIANCE", "TCS"]
    
    manager_instance = mock_manager.return_value
    
    result = runner.invoke(app, ["download", "nifty50"])
    
    assert result.exit_code == 0
    assert "Downloading data for 2 symbols in nifty50..." in result.stdout
    assert "Download complete." in result.stdout
    manager_instance.download_many.assert_called_once_with(["RELIANCE", "TCS"])


@patch("atlas.cli.commands.settings")
@patch("os.access")
def test_validate(mock_access, mock_settings):
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    
    mock_settings.BASE_DIR = mock_path
    mock_settings.DATA_DIR = mock_path
    mock_settings.UNIVERSE_DIR = mock_path
    
    mock_access.return_value = True
    
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "Validation passed. All systems go." in result.stdout


@patch("atlas.cli.commands.UniverseProvider")
@patch("atlas.cli.commands.MarketDataProvider")
@patch("atlas.cli.commands.RankingEngine")
@patch("atlas.cli.commands.ReportGenerator")
def test_scan_orchestration(mock_report_gen, mock_ranking, mock_mdp, mock_uni_prov):
    uni_instance = mock_uni_prov.return_value
    uni_instance.get.return_value = ["RELIANCE"]
    
    mdp_instance = mock_mdp.return_value
    # By returning an empty dataframe, we safely bypass all indicator calculations in the loop
    mdp_instance.get.return_value = pd.DataFrame() 
    
    ranking_instance = mock_ranking.return_value
    ranking_instance.rank.return_value = pd.DataFrame()
    
    report_instance = mock_report_gen.return_value
    report_instance.generate.return_value = {}
    report_instance.to_text.return_value = "MOCK REPORT GENERATED"
    
    result = runner.invoke(app, ["scan", "nifty50"])
    
    assert result.exit_code == 0
    assert "Starting scan for universe: nifty50" in result.stdout
    assert "Scanning 1 symbols..." in result.stdout
    
    # Because it returns an empty DF, the loop triggers `if df.empty: continue`
    # Therefore, "No stocks successfully scanned" should appear, bypassing RankingEngine
    assert "No stocks successfully scanned." in result.stdout


@patch("atlas.cli.commands.UniverseProvider")
@patch("atlas.cli.commands.MarketDataProvider")
@patch("atlas.cli.commands.RankingEngine")
@patch("atlas.cli.commands.ReportGenerator")
# We need to mock indicators/scanners if we want to pass a mock dataframe and have it survive the loop
@patch("atlas.cli.commands.EMAIndicator")
@patch("atlas.cli.commands.ATRIndicator")
@patch("atlas.cli.commands.RelativeVolumeIndicator")
@patch("atlas.cli.commands.HighLowIndicator")
@patch("atlas.cli.commands.RelativeStrengthIndicator")
@patch("atlas.cli.commands.MomentumScoreIndicator")
@patch("atlas.cli.commands.InstitutionalScanner")
@patch("atlas.cli.commands.MomentumScanner")
@patch("atlas.cli.commands.VCPScanner")
def test_full_scan_orchestration_success(
    mock_vcp, mock_mom, mock_inst,
    mock_ms, mock_rs, mock_hl, mock_rvol, mock_atr, mock_ema,
    mock_report_gen, mock_ranking, mock_mdp, mock_uni_prov
):
    # This test proves orchestration wires ranking and reporting if a stock survives
    uni_instance = mock_uni_prov.return_value
    uni_instance.get.return_value = ["RELIANCE"]
    
    mdp_instance = mock_mdp.return_value
    mdp_instance.get.return_value = pd.DataFrame({"dummy": [1]})
    
    # Ensure scanners return something so it records True
    mock_inst.return_value.scan.return_value = pd.DataFrame({"dummy": [1]})
    mock_mom.return_value.scan.return_value = pd.DataFrame({"dummy": [1]})
    mock_vcp.return_value.scan.return_value = pd.DataFrame({"dummy": [1]})
    
    # Mock indicator calculations to just return the dataframe
    mock_ema.return_value.calculate.side_effect = lambda df: df
    mock_atr.return_value.calculate.side_effect = lambda df: df
    mock_rvol.return_value.calculate.side_effect = lambda df: df
    mock_hl.return_value.calculate.side_effect = lambda df: df
    mock_rs.return_value.calculate.side_effect = lambda df, b: df
    mock_ms.return_value.calculate.side_effect = lambda df: df
    
    ranking_instance = mock_ranking.return_value
    ranking_instance.rank.return_value = pd.DataFrame({"Rank": [1], "Symbol": ["RELIANCE"]})
    
    report_instance = mock_report_gen.return_value
    report_instance.generate.return_value = {}
    report_instance.to_text.return_value = "MOCK REPORT GENERATED"
    
    result = runner.invoke(app, ["scan", "nifty50"])
    
    assert result.exit_code == 0
    assert "MOCK REPORT GENERATED" in result.stdout
    assert "Starting scan for universe: nifty50" in result.stdout
    
    ranking_instance.rank.assert_called_once()
    report_instance.generate.assert_called_once()
    report_instance.to_text.assert_called_once()
