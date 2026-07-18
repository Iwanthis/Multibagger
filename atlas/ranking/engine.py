"""
Ranking Engine

Combines boolean outputs from multiple scanners to assign a composite
score and rank to a list of stocks.
"""
import logging
import copy
from typing import List, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


class RankingError(Exception):
    """Raised when ranking engine validation fails."""
    pass


class RankingEngine:
    """
    Ranks stocks based on a configurable weighted scoring system of their
    scanner results.
    """

    def __init__(self, weights: Dict[str, int] = None) -> None:
        """
        Initialize the RankingEngine.

        Args:
            weights (Dict[str, int], optional): Mapping of scanner names to their score weight.
                Defaults to:
                {
                    "institutional": 30,
                    "momentum": 40,
                    "vcp": 20,
                    "breakout": 10
                }
        """
        if weights is None:
            self.weights = {
                "institutional": 30,
                "momentum": 40,
                "vcp": 20,
                "breakout": 10
            }
        else:
            self.weights = weights
            
        logger.debug(f"Initialized RankingEngine with weights: {self.weights}")

    def rank(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Calculate scores and rank the stocks.

        Args:
            results (List[Dict[str, Any]]): A list of dictionaries containing
                scanner boolean results for each stock.

        Returns:
            pd.DataFrame: A dataframe containing Rank, Symbol, Score, and all scanner columns,
                          sorted by Score (descending) and Symbol (ascending).
            
        Raises:
            RankingError: If input is empty, missing required keys, or contains duplicate symbols.
        """
        if not results:
            logger.error("Ranking validation failed: Input results list is empty.")
            raise RankingError("Input results list cannot be empty.")

        # Create a deep copy to ensure we never modify the input dictionaries
        results_copy = copy.deepcopy(results)

        required_keys = {"symbol"}.union(self.weights.keys())
        symbols_seen = set()

        # Validate input structure
        for row in results_copy:
            # Check required keys
            missing_keys = required_keys - set(row.keys())
            if missing_keys:
                logger.error(f"Missing required keys in row {row}: {missing_keys}")
                raise RankingError(f"Missing required keys: {missing_keys}")
                
            # Check duplicate symbols
            symbol = row["symbol"]
            if symbol in symbols_seen:
                logger.error(f"Duplicate symbol found: {symbol}")
                raise RankingError(f"Duplicate symbol: {symbol}")
            symbols_seen.add(symbol)
            
            # Calculate score
            score = 0
            for scanner, weight in self.weights.items():
                if row.get(scanner):
                    score += weight
            row["Score"] = score

        logger.info(f"Ranking {len(results_copy)} stocks...")

        # Convert to DataFrame
        df = pd.DataFrame(results_copy)
        
        # Capitalize scanner column names dynamically
        rename_map = {"symbol": "Symbol"}
        for scanner in self.weights.keys():
            if scanner.lower() == "vcp":
                rename_map[scanner] = "VCP"
            else:
                rename_map[scanner] = scanner.capitalize()
                
        df = df.rename(columns=rename_map)
        
        # Sort by Score (Descending), then Symbol (Ascending)
        df = df.sort_values(by=["Score", "Symbol"], ascending=[False, True])
        
        # Assign Rank starting at 1
        df["Rank"] = range(1, len(df) + 1)
        
        # Reorder columns to put Rank, Symbol, Score first
        scanner_cols = [rename_map[k] for k in self.weights.keys()]
        final_cols = ["Rank", "Symbol", "Score"] + scanner_cols
        
        df = df[final_cols].reset_index(drop=True)
        
        return df
