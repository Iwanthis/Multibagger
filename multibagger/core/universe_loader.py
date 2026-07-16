from pathlib import Path

import pandas as pd

from multibagger.config.settings import UNIVERSE_DIR


class UniverseLoader:
    """
    Loads a list of symbols from a universe CSV.

    Example
    -------
    loader = UniverseLoader("nifty500")
    symbols = loader.load()
    """

    def __init__(self, universe: str):
        self.file = UNIVERSE_DIR / f"{universe}.csv"

    def load(self):

        if not self.file.exists():
            raise FileNotFoundError(self.file)

        df = pd.read_csv(self.file)

        if "Symbol" not in df.columns:
            raise ValueError("Universe must contain a 'Symbol' column.")

        symbols = (
            df["Symbol"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        return sorted(symbols)