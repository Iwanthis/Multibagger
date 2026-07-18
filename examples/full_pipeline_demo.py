"""
End-to-End Integration Test for Atlas Framework.

This script demonstrates loading data and running the full pipeline of indicators.
"""
import logging
import sys
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("atlas.integration")

from atlas.providers import MarketDataProvider, DownloadManager, ProviderError
from atlas.indicators import (
    EMAIndicator,
    ATRIndicator,
    RelativeVolumeIndicator,
    HighLowIndicator,
    RelativeStrengthIndicator,
    MomentumScoreIndicator
)

def main():
    logger.info("Starting End-to-End Integration Test")
    
    # Instantiate Providers
    downloader = DownloadManager()
    data_provider = MarketDataProvider()
    
    stock_symbol = "RELIANCE"
    benchmark_symbol = "^NSEI" # Nifty 50
    
    try:
        # Download data to ensure it's available locally
        logger.info(f"Ensuring {benchmark_symbol} data is available...")
        downloader.download(benchmark_symbol, period="5y")
        
        logger.info(f"Ensuring {stock_symbol} data is available...")
        downloader.download(stock_symbol, period="5y")
        
        # 1. Load data
        logger.info(f"Loading {stock_symbol} data...")
        stock_data = data_provider.get(stock_symbol)
        logger.info(f"Loaded {len(stock_data)} rows for {stock_symbol}")
        
        logger.info("Loading benchmark data...")
        benchmark_data = data_provider.get(benchmark_symbol)
        
        # 2. Calculate EMAs
        logger.info("Calculating EMA20...")
        stock_data = EMAIndicator(period=20).calculate(stock_data)
        
        logger.info("Calculating EMA50...")
        stock_data = EMAIndicator(period=50).calculate(stock_data)
        
        logger.info("Calculating EMA200...")
        stock_data = EMAIndicator(period=200).calculate(stock_data)
        
        # 3. Calculate ATR
        logger.info("Calculating ATR14...")
        stock_data = ATRIndicator(period=14).calculate(stock_data)
        
        # 4. Calculate RVOL
        logger.info("Calculating RVOL20...")
        stock_data = RelativeVolumeIndicator(period=20).calculate(stock_data)
        
        # 5. Calculate High/Low
        logger.info("Calculating High/Low 252...")
        stock_data = HighLowIndicator(period=252).calculate(stock_data)
        
        # 6 & 7. Calculate Relative Strength
        logger.info("Calculating RS90...")
        # Since raw market data might have missing days, align them by Date first
        aligned_df = pd.merge(stock_data, benchmark_data, on="Date", how="inner", suffixes=("", "_bench"))
        
        # Extract the aligned dataframes and reset index
        aligned_stock = stock_data[stock_data["Date"].isin(aligned_df["Date"])].reset_index(drop=True)
        aligned_bench = benchmark_data[benchmark_data["Date"].isin(aligned_df["Date"])].reset_index(drop=True)
        
        stock_data = aligned_stock
        benchmark_data = aligned_bench
        
        logger.info(f"Aligned datasets to {len(stock_data)} rows to satisfy RS requirements.")
        
        stock_data = RelativeStrengthIndicator(period=90).calculate(stock_data, benchmark_data)
        
        # 8. Calculate Momentum Score
        logger.info("Calculating Momentum Score...")
        stock_data = MomentumScoreIndicator().calculate(stock_data)
        
        # 9. Display final 10 rows
        columns_to_show = [
            "Date", "Close", "EMA20", "EMA50", "EMA200", 
            "ATR14", "RVOL20", "HIGH252", "LOW252", "RS90", "MomentumScore"
        ]
        
        logger.info("\n--- Final 10 Rows ---")
        print(stock_data[columns_to_show].tail(10).to_string(index=False))
        
        # Final Summary
        print("\n✓ Market data loaded")
        print("✓ EMA calculated")
        print("✓ ATR calculated")
        print("✓ RVOL calculated")
        print("✓ High/Low calculated")
        print("✓ Relative Strength calculated")
        print("✓ Momentum Score calculated")
        print("✓ Pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
