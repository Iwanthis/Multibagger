from pathlib import Path
import pandas as pd

from multibagger.config.settings import UNIVERSE_DIR


class DataLoader:
    """
    Loads an entire universe into memory.

    Example:
        loader = DataLoader("nifty500")
        stocks = loader.load()
    """

    REQUIRED_COLUMNS = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    def __init__(self, universe: str):

        self.universe = universe
        self.folder = UNIVERSE_DIR / universe

    def load(self):

        if not self.folder.exists():
            raise FileNotFoundError(
                f"Universe '{self.universe}' not found."
            )

        stocks = {}

        for file in sorted(self.folder.glob("*.csv")):

            df = pd.read_csv(file)

            missing = [
                col
                for col in self.REQUIRED_COLUMNS
                if col not in df.columns
            ]

            if missing:
                print(f"Skipping {file.name}: Missing {missing}")
                continue

            df["Date"] = pd.to_datetime(df["Date"])

            df.sort_values("Date", inplace=True)

            df.reset_index(drop=True, inplace=True)

            stocks[file.stem] = df

        return stocks