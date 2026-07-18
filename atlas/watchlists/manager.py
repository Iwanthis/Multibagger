from pathlib import Path
from typing import List
import pandas as pd
from datetime import datetime

from atlas.config import settings
from atlas.watchlists.exceptions import WatchlistError

class WatchlistManager:
    """Manages creation, modification, and loading of watchlists."""
    
    def __init__(self, watchlists_dir: Path = settings.WATCHLISTS_DIR):
        self.watchlists_dir = watchlists_dir
        self.watchlists_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_path(self, name: str) -> Path:
        # Sanitize filename (e.g. lowercase and trim)
        safe_name = name.lower().strip()
        return self.watchlists_dir / f"{safe_name}.csv"
        
    def create(self, name: str) -> None:
        """Create a new, empty watchlist."""
        path = self._get_path(name)
        if path.exists():
            raise WatchlistError(f"Watchlist '{name}' already exists.")
            
        try:
            df = pd.DataFrame(columns=["DateAdded", "Symbol"])
            df.to_csv(path, index=False, encoding="utf-8")
        except Exception as e:
            raise WatchlistError(f"Failed to create watchlist '{name}': {e}")
            
    def exists(self, name: str) -> bool:
        """Check if a watchlist exists."""
        return self._get_path(name).exists()
        
    def list(self) -> List[str]:
        """List all available watchlists."""
        if not self.watchlists_dir.exists():
            return []
            
        watchlists = []
        for file in self.watchlists_dir.glob("*.csv"):
            watchlists.append(file.stem)
        return sorted(watchlists)
        
    def load(self, name: str) -> pd.DataFrame:
        """Load a watchlist dataframe by name."""
        path = self._get_path(name)
        if not path.exists():
            raise WatchlistError(f"Watchlist '{name}' does not exist.")
            
        try:
            return pd.read_csv(path)
        except Exception as e:
            raise WatchlistError(f"Failed to load watchlist '{name}': {e}")
            
    def save(self, name: str, dataframe: pd.DataFrame) -> None:
        """Save a dataframe to the specified watchlist. Does not mutate the input dataframe."""
        path = self._get_path(name)
        try:
            df = dataframe.copy()
            if not df.empty:
                # Ensure it remains sorted alphabetically by Symbol
                df = df.sort_values(by="Symbol")
            df.to_csv(path, index=False, encoding="utf-8")
        except Exception as e:
            raise WatchlistError(f"Failed to save watchlist '{name}': {e}")
            
    def add(self, name: str, symbol: str) -> None:
        """Add a symbol to the specified watchlist."""
        if not self.exists(name):
            raise WatchlistError(f"Watchlist '{name}' does not exist.")
            
        symbol = symbol.strip().upper()
        df = self.load(name)
        
        if symbol in df["Symbol"].values:
            # Adding a symbol already present must not create duplicates
            return
            
        try:
            new_row = pd.DataFrame({
                "DateAdded": [datetime.now().strftime("%Y-%m-%d")],
                "Symbol": [symbol]
            })
            
            combined_df = pd.concat([df, new_row], ignore_index=True)
            self.save(name, combined_df)
        except Exception as e:
            raise WatchlistError(f"Failed to add symbol to watchlist '{name}': {e}")
            
    def remove(self, name: str, symbol: str) -> None:
        """Remove a symbol from the specified watchlist."""
        if not self.exists(name):
            raise WatchlistError(f"Watchlist '{name}' does not exist.")
            
        symbol = symbol.strip().upper()
        df = self.load(name)
        
        if symbol not in df["Symbol"].values:
            # Removing a symbol that does not exist must not raise an exception
            return
            
        try:
            df = df[df["Symbol"] != symbol]
            self.save(name, df)
        except Exception as e:
            raise WatchlistError(f"Failed to remove symbol from watchlist '{name}': {e}")
            
    def contains(self, name: str, symbol: str) -> bool:
        """Check if a symbol is in the specified watchlist."""
        if not self.exists(name):
            return False
        
        symbol = symbol.strip().upper()
        try:
            df = self.load(name)
            return symbol in df["Symbol"].values
        except WatchlistError:
            return False
