import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime

from atlas.reporting.chart_generator import ChartGenerator, ChartGenerationError


@pytest.fixture
def sample_market_data():
    dates = pd.date_range(start="2023-01-01", periods=200, freq="D")
    df = pd.DataFrame({
        "Open": [100.0] * 200,
        "High": [105.0] * 200,
        "Low": [95.0] * 200,
        "Close": [102.0] * 200,
        "Volume": [10000] * 200,
        "EMA20": [101.0] * 200,
        "EMA50": [100.5] * 200,
        "EMA200": [99.0] * 200,
        "HIGH252": [110.0] * 200
    }, index=dates)
    return df


def test_chart_generation_success(sample_market_data, tmp_path):
    generator = ChartGenerator()
    output_path = tmp_path / "charts" / "TEST.png"
    
    returned_path = generator.generate_chart(sample_market_data, "TEST", output_path)
    
    assert returned_path == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_directory_creation(sample_market_data, tmp_path):
    generator = ChartGenerator()
    # deeply nested path
    output_path = tmp_path / "deep" / "nested" / "dir" / "charts" / "TEST.png"
    assert not output_path.parent.exists()
    
    generator.generate_chart(sample_market_data, "TEST", output_path)
    
    assert output_path.parent.exists()
    assert output_path.exists()


def test_missing_required_columns(sample_market_data, tmp_path):
    generator = ChartGenerator()
    output_path = tmp_path / "TEST.png"
    
    df_missing = sample_market_data.drop(columns=["EMA20"])
    
    with pytest.raises(ChartGenerationError, match="Missing columns \\['EMA20'\\]"):
        generator.generate_chart(df_missing, "TEST", output_path)


def test_empty_dataframe(tmp_path):
    generator = ChartGenerator()
    output_path = tmp_path / "TEST.png"
    
    empty_df = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume", "EMA20", "EMA50", "EMA200", "HIGH252"])
    
    with pytest.raises(ChartGenerationError, match="Dataframe is empty"):
        generator.generate_chart(empty_df, "TEST", output_path)


def test_dataframe_immutability(sample_market_data, tmp_path):
    generator = ChartGenerator()
    output_path = tmp_path / "TEST.png"
    
    original = sample_market_data.copy(deep=True)
    
    generator.generate_chart(sample_market_data, "TEST", output_path)
    
    pd.testing.assert_frame_equal(sample_market_data, original)
