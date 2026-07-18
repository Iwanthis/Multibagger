"""
Report Generator

Converts the output of the Ranking Engine into a standardized reporting format.
"""
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class ReportError(Exception):
    """Raised when report generation validation fails."""
    pass


class ReportGenerator:
    """
    Generates presentation-ready reports from ranking engine dataframes.
    """

    REQUIRED_COLUMNS = ["Rank", "Symbol", "Score"]

    def __init__(self) -> None:
        """Initialize the ReportGenerator."""
        logger.debug("Initialized ReportGenerator")

    def generate(self, ranking_dataframe: pd.DataFrame, universe_name: str = "Unknown") -> Dict[str, Any]:
        """
        Generate a summary report from the ranking dataframe.

        Args:
            ranking_dataframe (pd.DataFrame): The output from the RankingEngine.
            universe_name (str): The name of the scanned universe. Defaults to "Unknown".

        Returns:
            Dict[str, Any]: A dictionary containing summary statistics and the dataframe.
            
        Raises:
            ReportError: If the dataframe is empty or missing required columns.
        """
        if ranking_dataframe is None or ranking_dataframe.empty:
            logger.error("Report generation failed: dataframe is empty")
            raise ReportError("Input dataframe cannot be empty.")
            
        missing = [col for col in self.REQUIRED_COLUMNS if col not in ranking_dataframe.columns]
        if missing:
            logger.error(f"Missing required columns for ReportGenerator: {missing}")
            raise ReportError(f"Missing required columns: {missing}")

        logger.info(f"Generating report for universe: {universe_name}")
        
        # We assume all rows in the dataframe were scanned.
        # Qualified stocks are those with a Score > 0.
        stocks_scanned = len(ranking_dataframe)
        qualified_df = ranking_dataframe[ranking_dataframe["Score"] > 0]
        qualified = len(qualified_df)
        
        top_score = 0
        average_score = 0.0
        
        if qualified > 0:
            top_score = float(qualified_df["Score"].max())
            average_score = float(qualified_df["Score"].mean())
            
        # Use current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        report = {
            "date": current_date,
            "universe": universe_name,
            "stocks_scanned": stocks_scanned,
            "qualified": qualified,
            "top_score": top_score,
            "average_score": round(average_score, 2),
            "results": ranking_dataframe.copy()
        }
        
        return report

    def to_text(self, report: Dict[str, Any]) -> str:
        """
        Format the report dictionary into a readable text string.

        Args:
            report (Dict[str, Any]): The generated report dictionary.

        Returns:
            str: The formatted text report.
        """
        lines = []
        lines.append("====================================")
        lines.append("MULTIBAGGER DAILY REPORT")
        lines.append("====================================")
        lines.append(f"Date: {report.get('date', '')}")
        lines.append(f"Universe: {report.get('universe', '')}")
        lines.append(f"Stocks Scanned: {report.get('stocks_scanned', 0)}")
        lines.append(f"Qualified: {report.get('qualified', 0)}")
        lines.append(f"Top Score: {report.get('top_score', 0)}")
        lines.append(f"Average Score: {report.get('average_score', 0.0)}")
        lines.append("------------------------------------")
        
        df = report.get("results")
        if df is not None and not df.empty:
            # We want to show Rank, Symbol, Score as per the requested formatting
            cols = [c for c in ["Rank", "Symbol", "Score"] if c in df.columns]
            df_string = df[cols].to_string(index=False)
            lines.append(df_string)
        else:
            lines.append("No results.")
            
        lines.append("------------------------------------")
        
        return "\n".join(lines)

    def export_csv(self, report: Dict[str, Any], output_path: Path) -> Path:
        """
        Export the ranked stocks to a CSV file.
        
        Args:
            report (Dict[str, Any]): The generated report dictionary.
            output_path (Path): The path where the CSV should be saved.
            
        Returns:
            Path: The path to the saved CSV file.
            
        Raises:
            ReportError: If exporting fails.
        """
        df = report.get("results")
        if df is None:
            raise ReportError("Report dictionary is missing 'results' dataframe.")
            
        try:
            # Ensure the directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Requested exact column order
            columns = ["Rank", "Symbol", "Score", "Institutional", "Momentum", "VCP"]
            
            # Start with an empty dataframe that enforces the column order
            export_df = pd.DataFrame(columns=columns)
            
            if not df.empty:
                temp_df = df.copy()
                
                # Standardize column casing
                rename_map = {
                    "symbol": "Symbol",
                    "institutional": "Institutional",
                    "momentum": "Momentum",
                    "vcp": "VCP",
                    "rank": "Rank",
                    "score": "Score"
                }
                temp_df = temp_df.rename(columns=rename_map)
                
                # Find which of the requested columns are actually available
                available_cols = [c for c in columns if c in temp_df.columns]
                
                # Concatenate vertically
                if available_cols:
                    export_df = pd.concat([export_df, temp_df[available_cols]], ignore_index=True)
            
            # Save using utf-8 encoding as required
            export_df[columns].to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Report exported to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export CSV report: {e}")
            raise ReportError(f"Failed to export CSV report: {e}")

    def export_excel(self, report: Dict[str, Any], output_path: Path) -> Path:
        """
        Export the ranked stocks to a formatted Excel workbook.
        
        Args:
            report (Dict[str, Any]): The generated report dictionary.
            output_path (Path): The path where the Excel file should be saved.
            
        Returns:
            Path: The path to the saved Excel file.
            
        Raises:
            ReportError: If exporting fails.
        """
        df = report.get("results")
        if df is None:
            raise ReportError("Report dictionary is missing 'results' dataframe.")
            
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            columns = ["Rank", "Symbol", "Score", "Institutional", "Momentum", "VCP"]
            export_df = pd.DataFrame(columns=columns)
            
            if not df.empty:
                temp_df = df.copy()
                rename_map = {
                    "symbol": "Symbol",
                    "institutional": "Institutional",
                    "momentum": "Momentum",
                    "vcp": "VCP",
                    "rank": "Rank",
                    "score": "Score"
                }
                temp_df = temp_df.rename(columns=rename_map)
                available_cols = [c for c in columns if c in temp_df.columns]
                if available_cols:
                    export_df = pd.concat([export_df, temp_df[available_cols]], ignore_index=True)

            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                export_df[columns].to_excel(writer, sheet_name='Daily Scan', index=False)
                
                workbook = writer.book
                worksheet = writer.sheets['Daily Scan']
                
                from openpyxl.styles import Font, Alignment, PatternFill
                from openpyxl.formatting.rule import CellIsRule

                # 5. Freeze the first row
                worksheet.freeze_panes = "A2"
                
                # 6. Enable AutoFilter
                last_col_letter = chr(ord('A') + len(columns) - 1)
                worksheet.auto_filter.ref = f"A1:{last_col_letter}{max(1, len(export_df)+1)}"
                
                # Formatting objects
                bold_font = Font(bold=True)
                center_align = Alignment(horizontal='center', vertical='center')
                
                for col_idx, col_name in enumerate(columns, start=1):
                    # 7. Bold header
                    header_cell = worksheet.cell(row=1, column=col_idx)
                    header_cell.font = bold_font
                    
                    if col_name != "Symbol":
                        header_cell.alignment = center_align
                
                # Column adjustments and data alignment
                for col_idx, col_name in enumerate(columns, start=1):
                    col_letter = chr(ord('A') + col_idx - 1)
                    
                    # 4. Auto-adjust column widths
                    max_length = len(col_name)
                    if not export_df.empty:
                        col_values = export_df[col_name].astype(str)
                        max_length = max(max_length, col_values.map(len).max())
                    
                    worksheet.column_dimensions[col_letter].width = max_length + 2
                    
                    # 8. Center align every column except Symbol
                    if col_name != "Symbol":
                        for row_idx in range(2, len(export_df) + 2):
                            worksheet.cell(row=row_idx, column=col_idx).alignment = center_align
                
                # 9. Apply conditional formatting to Score column (C)
                if not export_df.empty:
                    score_range = f"C2:C{len(export_df)+1}"
                    
                    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                    yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                    blue_fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
                    
                    worksheet.conditional_formatting.add(
                        score_range,
                        CellIsRule(operator='greaterThanOrEqual', formula=['70'], fill=green_fill)
                    )
                    worksheet.conditional_formatting.add(
                        score_range,
                        CellIsRule(operator='between', formula=['40', '69'], fill=yellow_fill)
                    )
                    worksheet.conditional_formatting.add(
                        score_range,
                        CellIsRule(operator='between', formula=['1', '39'], fill=blue_fill)
                    )
                    
            logger.info(f"Report exported to Excel: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export Excel report: {e}")
            raise ReportError(f"Failed to export Excel report: {e}")

    def append_history(self, report: Dict[str, Any], history_path: Path) -> Path:
        """
        Append the daily scan results to a historical archive CSV.
        
        Args:
            report (Dict[str, Any]): The generated report dictionary.
            history_path (Path): The path to the master history CSV.
            
        Returns:
            Path: The path to the history file.
        """
        df = report.get("results")
        if df is None:
            raise ReportError("Report dictionary is missing 'results' dataframe.")
            
        try:
            history_path.parent.mkdir(parents=True, exist_ok=True)
            
            columns = ["ScanDate", "Rank", "Symbol", "Score", "Institutional", "Momentum", "VCP"]
            new_data = pd.DataFrame(columns=columns)
            
            if not df.empty:
                temp_df = df.copy()
                rename_map = {
                    "symbol": "Symbol",
                    "institutional": "Institutional",
                    "momentum": "Momentum",
                    "vcp": "VCP",
                    "rank": "Rank",
                    "score": "Score"
                }
                temp_df = temp_df.rename(columns=rename_map)
                temp_df["ScanDate"] = report.get("date", datetime.now().strftime("%Y-%m-%d"))
                
                available_cols = [c for c in columns if c in temp_df.columns]
                new_data = pd.concat([new_data, temp_df[available_cols]], ignore_index=True)
            
            if history_path.exists():
                history_df = pd.read_csv(history_path)
                # Ensure existing history has the required columns
                for col in columns:
                    if col not in history_df.columns:
                        history_df[col] = None
                        
                combined_df = pd.concat([history_df, new_data], ignore_index=True)
                
                # Drop duplicates for the same ScanDate and Symbol
                # This ensures we don't duplicate stocks if we run multiple scans in one day
                combined_df = combined_df.drop_duplicates(subset=["ScanDate", "Symbol"], keep="last")
                
                # Preserve chronological order
                combined_df = combined_df.sort_values(by=["ScanDate", "Rank"])
            else:
                combined_df = new_data
                if not combined_df.empty:
                    combined_df = combined_df.sort_values(by=["ScanDate", "Rank"])
            
            # Export back to CSV
            combined_df[columns].to_csv(history_path, index=False, encoding="utf-8")
            logger.info(f"Scan history appended to {history_path}")
            return history_path
            
        except Exception as e:
            logger.error(f"Failed to append to scan history: {e}")
            raise ReportError(f"Failed to append to scan history: {e}")
