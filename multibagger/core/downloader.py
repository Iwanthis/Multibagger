from pathlib import Path
import time

import yfinance as yf
from tqdm import tqdm

from multibagger.config.settings import DAILY_DATA_DIR
from multibagger.core.universe_loader import UniverseLoader


class MarketDataDownloader:

    def __init__(self):

        DAILY_DATA_DIR.mkdir(parents=True, exist_ok=True)

    def download_symbol(self, symbol: str, force=False):

        file = DAILY_DATA_DIR / f"{symbol}.csv"

        # Skip if already downloaded
        if file.exists() and not force:
            return "skipped"

        yahoo_symbol = f"{symbol}.NS"

        # Retry 3 times
        for attempt in range(3):

            try:

                df = yf.download(
                    yahoo_symbol,
                    period="max",
                    interval="1d",
                    progress=False,
                    auto_adjust=False,
                )

                if df.empty:
                    return "failed"

                df.reset_index(inplace=True)

                df.to_csv(file, index=False)

                return "downloaded"

            except Exception:

                time.sleep(1)

        return "failed"

    def download_universe(self, universe: str, force=False):

        symbols = UniverseLoader(universe).load()

        downloaded = 0
        skipped = 0
        failed = 0

        for symbol in tqdm(symbols):

            result = self.download_symbol(symbol, force)

            if result == "downloaded":
                downloaded += 1

            elif result == "skipped":
                skipped += 1

            else:
                failed += 1

        print()
        print("=" * 60)
        print("DOWNLOAD COMPLETE")
        print("=" * 60)

        print(f"Downloaded : {downloaded}")
        print(f"Skipped    : {skipped}")
        print(f"Failed     : {failed}")