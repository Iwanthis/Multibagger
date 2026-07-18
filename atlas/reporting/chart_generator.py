import logging
import pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class ChartGenerationError(Exception):
    """Exception raised when chart generation fails."""
    pass

class ChartGenerator:
    """Generates technical analysis charts for qualified stocks."""
    
    REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume", "EMA20", "EMA50", "EMA200", "HIGH252"]
    
    def generate_chart(self, data: pd.DataFrame, symbol: str, output_path: Path) -> Path:
        """
        Generates and saves a technical chart for the given stock data.
        
        Args:
            data (pd.DataFrame): The stock market data containing required indicators.
            symbol (str): The stock symbol.
            output_path (Path): Path to save the PNG image.
            
        Returns:
            Path: The path to the saved image.
            
        Raises:
            ChartGenerationError: If data is invalid or generation fails.
        """
        if data is None or data.empty:
            raise ChartGenerationError(f"Cannot generate chart for {symbol}: Dataframe is empty.")
            
        missing = [col for col in self.REQUIRED_COLUMNS if col not in data.columns]
        if missing:
            raise ChartGenerationError(f"Cannot generate chart for {symbol}: Missing columns {missing}")
            
        try:
            # Ensure we don't mutate the input dataframe
            df = data.copy()
            
            # Use the last 150 trading days for a readable chart
            df = df.tail(150)
            if df.empty:
                raise ChartGenerationError(f"Not enough data for {symbol} after filtering.")
                
            # Create a figure with 2 subplots (Price and Volume)
            # GridSpec ratio 3:1 for Price vs Volume
            fig, (ax_price, ax_vol) = plt.subplots(
                2, 1, 
                figsize=(12, 8), 
                gridspec_kw={'height_ratios': [3, 1]},
                sharex=True
            )
            
            fig.suptitle(f"{symbol} - Technical Analysis", fontsize=16, fontweight='bold')
            
            # Convert index to a range for plotting to avoid weekend gaps, or just plot directly
            x_dates = pd.to_datetime(df.index) if isinstance(df.index, pd.DatetimeIndex) else df.index
            
            # --- Price Subplot (Candlesticks) ---
            colors = ['green' if close >= open_p else 'red' for close, open_p in zip(df['Close'], df['Open'])]
            # Wicks
            ax_price.vlines(x_dates, df['Low'], df['High'], color=colors, linewidth=1)
            # Bodies
            ax_price.bar(x_dates, abs(df['Close'] - df['Open']), bottom=df[['Open', 'Close']].min(axis=1), color=colors, width=0.8, edgecolor=colors, label='Price')

            ax_price.plot(x_dates, df['EMA20'], label='EMA 20', color='#27ae60', linestyle='--', linewidth=1.5)
            ax_price.plot(x_dates, df['EMA50'], label='EMA 50', color='#f39c12', linestyle='-.', linewidth=1.5)
            ax_price.plot(x_dates, df['EMA200'], label='EMA 200', color='#c0392b', linestyle=':', linewidth=1.5)
            ax_price.plot(x_dates, df['HIGH252'], label='52W High', color='#8e44ad', linestyle='-', linewidth=1, alpha=0.6)
            
            # Buy Signal Marker on the latest candle (since it's a qualified stock)
            latest_date = x_dates[-1]
            latest_close = df['Close'].iloc[-1]
            ax_price.plot(latest_date, latest_close, marker='^', color='green', markersize=12, label='Buy Signal')
            
            # Highlight latest close
            ax_price.annotate(f"{latest_close:.2f}", 
                              xy=(latest_date, latest_close),
                              xytext=(10, 0), textcoords='offset points',
                              bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1),
                              fontsize=10, fontweight='bold', va='center')
                              
            ax_price.set_ylabel('Price', fontsize=12)
            ax_price.legend(loc='upper left', fontsize=10)
            ax_price.grid(True, linestyle='--', alpha=0.5)
            
            # --- Volume Subplot ---
            colors = ['green' if close >= open_p else 'red' for close, open_p in zip(df['Close'], df.get('Open', df['Close']))]
            ax_vol.bar(x_dates, df['Volume'], color=colors, alpha=0.7)
            ax_vol.set_ylabel('Volume', fontsize=12)
            ax_vol.set_xlabel('Date', fontsize=12)
            ax_vol.grid(True, linestyle='--', alpha=0.3)
            
            # Resize layout
            plt.tight_layout()
            
            # Export
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Generated chart for {symbol} at {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Chart generation failed for {symbol}: {e}")
            raise ChartGenerationError(f"Chart generation failed for {symbol}: {e}")
