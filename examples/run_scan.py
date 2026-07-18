"""
End-to-End Pipeline Demo

Runs the Atlas CLI scan command programmatically to validate
the end-to-end integration of all components.
"""
import sys
import logging
from typer.testing import CliRunner

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from atlas.cli.commands import app

if __name__ == "__main__":
    print("Starting End-to-End Pipeline Validation...")
    runner = CliRunner()
    
    # We will use 'watchlist' if it exists, or 'nifty50'
    print("\n--- Running: atlas scan test ---")
    result = runner.invoke(app, ["scan", "test"])
    
    print(result.stdout)
    if result.exception:
        print(f"Exception details: {result.exception}")
