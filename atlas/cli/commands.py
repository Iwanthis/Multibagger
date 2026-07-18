"""
Atlas Framework CLI

Provides command-line orchestration for the Atlas framework.
Handles orchestration of providers, indicators, scanners, rankers, and reporting.
"""
import logging
import os
import typer
from datetime import datetime


from atlas.providers.universe_provider import UniverseProvider
from atlas.providers.download_manager import DownloadManager
from atlas.providers.market_data_provider import MarketDataProvider
from atlas.indicators.ema import EMAIndicator
from atlas.indicators.atr import ATRIndicator
from atlas.indicators.relative_volume import RelativeVolumeIndicator
from atlas.indicators.high_low import HighLowIndicator
from atlas.indicators.relative_strength import RelativeStrengthIndicator
from atlas.indicators.momentum_score import MomentumScoreIndicator
from atlas.scanners.institutional import InstitutionalScanner
from atlas.scanners.momentum import MomentumScanner
from atlas.scanners.vcp import VCPScanner
from atlas.ranking.engine import RankingEngine
from atlas.reporting.report_generator import ReportGenerator
from atlas.config import settings

logger = logging.getLogger(__name__)

app = typer.Typer(help="Atlas Framework CLI")


@app.command()
def version():
    """Display the framework version."""
    typer.echo("Multibagger")
    typer.echo("Atlas Framework")
    typer.echo("")
    typer.echo("Version 0.1.0")


@app.command()
def list_universes():
    """Displays available universes."""
    try:
        provider = UniverseProvider()
        universes = provider.list()
        if not universes:
            typer.echo("No universes found.")
        else:
            for uni in universes:
                typer.echo(uni)
    except Exception as e:
        logger.error(f"Error listing universes: {e}")
        typer.echo(f"Error: {e}")


@app.command()
def download(universe: str):
    """Downloads or refreshes all symbols for the specified universe."""
    try:
        provider = UniverseProvider()
        symbols = provider.get(universe)
        
        manager = DownloadManager()
        typer.echo(f"Downloading data for {len(symbols)} symbols in {universe}...")
        manager.download_many(symbols)
        typer.echo("Download complete.")
    except Exception as e:
        logger.error(f"Download failed: {e}")
        typer.echo(f"Error: {e}")


@app.command()
def validate():
    """Checks required folders, configurations, and write permissions."""
    typer.echo("Validating Atlas configuration...")
    issues = []
    
    paths_to_check = {
        "Base Directory": settings.PROJECT_ROOT,
        "Data Directory": settings.DATA_DIR,
        "Universe Directory": settings.UNIVERSE_DIR
    }
    
    for name, p in paths_to_check.items():
        if not p.exists():
            issues.append(f"{name} does not exist: {p}")
        elif not os.access(p, os.W_OK):
            issues.append(f"{name} is not writable: {p}")
                
    if not issues:
        typer.echo("Validation passed. All systems go.")
    else:
        typer.echo("Validation failed:")
        for issue in issues:
            typer.echo(f" - {issue}")


@app.command()
def scan(universe: str):
    """Runs the complete scan pipeline on a universe."""
    try:
        typer.echo(f"Starting scan for universe: {universe}")
        
        # 1. Universe
        uni_provider = UniverseProvider()
        symbols = uni_provider.get(universe)
        
        # 2. Data Provider
        data_provider = MarketDataProvider()
        
        benchmark_data = None
        try:
            benchmark_data = data_provider.get("^NSEI")
        except Exception as e:
            logger.warning(f"Could not load benchmark data (^NSEI) for RS calculation: {e}")
        
        # Initialize pipeline components
        ema20 = EMAIndicator(20)
        ema50 = EMAIndicator(50)
        ema200 = EMAIndicator(200)
        atr14 = ATRIndicator(14)
        rvol20 = RelativeVolumeIndicator(20)
        highlow = HighLowIndicator(252)
        rs90 = RelativeStrengthIndicator(90)
        momentum_score = MomentumScoreIndicator()
        
        institutional = InstitutionalScanner()
        momentum = MomentumScanner()
        vcp = VCPScanner()
        
        results = []
        
        typer.echo(f"Scanning {len(symbols)} symbols...")
        for sym in symbols:
            try:
                df = data_provider.get(sym)
                if df is None or df.empty:
                    continue
                    
                # Calculate Indicators
                df = ema20.calculate(df)
                df = ema50.calculate(df)
                df = ema200.calculate(df)
                df = atr14.calculate(df)
                df = rvol20.calculate(df)
                df = highlow.calculate(df)
                
                if benchmark_data is not None and not benchmark_data.empty:
                    try:
                        df = rs90.calculate(df, benchmark_data)
                    except Exception:
                        df["RS90"] = 0.0 
                else:
                    df["RS90"] = 0.0
                    
                df = momentum_score.calculate(df)
                
                # Execute Scanners
                inst_pass = institutional.scan_latest(df)
                mom_pass = momentum.scan_latest(df)
                vcp_pass = vcp.scan_latest(df)
                
                result_row = {
                    "symbol": sym,
                    "institutional": inst_pass,
                    "momentum": mom_pass,
                    "vcp": vcp_pass,
                    "breakout": vcp_pass  # Using VCP as breakout proxy based on prompt
                }
                
                results.append(result_row)
                
            except Exception as e:
                logger.debug(f"Skipping {sym} due to calculation error: {e}")
                
        if not results:
            typer.echo("No stocks successfully scanned.")
            return

        # 3. Ranking
        ranker = RankingEngine()
        ranked_df = ranker.rank(results)
        
        # 4. Reporting
        generator = ReportGenerator()
        report = generator.generate(ranked_df, universe_name=universe)
        
        typer.echo(generator.to_text(report))
        
        # 5. Export Reports
        current_date = datetime.now().strftime("%Y%m%d")
        csv_filename = f"multibagger_{current_date}.csv"
        excel_filename = f"multibagger_{current_date}.xlsx"
        csv_path = settings.REPORTS_DIR / csv_filename
        excel_path = settings.REPORTS_DIR / excel_filename
        history_path = settings.HISTORY_DIR / "scan_history.csv"
        
        try:
            exported_csv = generator.export_csv(report, csv_path)
            exported_excel = generator.export_excel(report, excel_path)
            updated_history = generator.append_history(report, history_path)
            
            try:
                rel_csv = exported_csv.relative_to(settings.PROJECT_ROOT)
                rel_excel = exported_excel.relative_to(settings.PROJECT_ROOT)
                rel_history = updated_history.relative_to(settings.PROJECT_ROOT)
                typer.echo(f"\nReports exported:\n{rel_csv.as_posix()}\n{rel_excel.as_posix()}")
                typer.echo(f"History updated:\n{rel_history.as_posix()}")
            except ValueError:
                typer.echo(f"\nReports exported:\n{exported_csv}\n{exported_excel}")
                typer.echo(f"History updated:\n{updated_history}")
        except Exception as e:
            logger.error(f"Export failed: {e}")
            typer.echo(f"\nExport failed: {e}")
        
    except Exception as e:
        logger.error(f"Scan orchestration failed: {e}")
        typer.echo(f"Scan failed: {e}")


# Watchlist CLI Commands
from atlas.watchlists import WatchlistManager, WatchlistError

watchlist_app = typer.Typer(help="Manage watchlists")
app.add_typer(watchlist_app, name="watchlist")

@app.command(name="watchlists")
def list_watchlists():
    """List all available watchlists."""
    manager = WatchlistManager()
    lists = manager.list()
    if not lists:
        typer.echo("No watchlists found.")
    else:
        typer.echo("Available Watchlists:")
        for name in lists:
            typer.echo(f" - {name}")

@watchlist_app.command(name="create")
def watchlist_create(name: str):
    """Create a new watchlist."""
    try:
        manager = WatchlistManager()
        manager.create(name)
        typer.echo(f"Created watchlist {name}")
    except WatchlistError as e:
        typer.echo(f"Error: {e}")

@watchlist_app.command(name="add")
def watchlist_add(name: str, symbol: str):
    """Add a symbol to a watchlist."""
    try:
        manager = WatchlistManager()
        manager.add(name, symbol)
        typer.echo(f"Added {symbol.upper()} to {name}")
    except WatchlistError as e:
        typer.echo(f"Error: {e}")

@watchlist_app.command(name="remove")
def watchlist_remove(name: str, symbol: str):
    """Remove a symbol from a watchlist."""
    try:
        manager = WatchlistManager()
        manager.remove(name, symbol)
        typer.echo(f"Removed {symbol.upper()} from {name}")
    except WatchlistError as e:
        typer.echo(f"Error: {e}")

@watchlist_app.command(name="show")
def watchlist_show(name: str):
    """Display the contents of a watchlist."""
    try:
        manager = WatchlistManager()
        df = manager.load(name)
        typer.echo(f"\n{name} Watchlist")
        if df.empty:
            typer.echo("(Empty)")
        else:
            for sym in df["Symbol"].values:
                typer.echo(sym)
    except WatchlistError as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()