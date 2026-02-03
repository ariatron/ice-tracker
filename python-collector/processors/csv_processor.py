"""CSV processing utilities."""
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CSVProcessor:
    """Process and clean CSV data files."""

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize a DataFrame."""
        # Remove empty rows and columns
        df = df.dropna(how="all", axis=0)
        df = df.dropna(how="all", axis=1)

        # Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # Strip whitespace from string columns
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

        return df

    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to lowercase with underscores."""
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")
        return df

    @staticmethod
    def detect_column_type(df: pd.DataFrame, col: str) -> str:
        """Detect the semantic type of a column."""
        col_lower = col.lower()

        # Date/time columns
        if any(x in col_lower for x in ["date", "time", "period", "month", "year"]):
            return "datetime"

        # Geographic columns
        if any(x in col_lower for x in ["state", "county", "city", "zip", "location"]):
            return "geography"

        # Count columns
        if any(x in col_lower for x in ["count", "total", "number", "arrests", "removals"]):
            return "numeric"

        # Categorical columns
        if df[col].nunique() < 50 and len(df) > 100:
            return "categorical"

        return "text"

    @staticmethod
    def convert_to_numeric(series: pd.Series, default: Optional[float] = None) -> pd.Series:
        """Convert a series to numeric, handling errors gracefully."""
        try:
            # Remove commas and other formatting
            if series.dtype == "object":
                series = series.str.replace(",", "").str.replace("$", "")

            return pd.to_numeric(series, errors="coerce").fillna(default if default is not None else 0)
        except Exception as e:
            logger.warning(f"Error converting to numeric: {e}")
            return series

    @staticmethod
    def standardize_state_codes(series: pd.Series) -> pd.Series:
        """Standardize state codes to 2-letter uppercase format."""
        # Map full state names to codes if needed
        state_map = {
            "alabama": "AL",
            "alaska": "AK",
            "arizona": "AZ",
            "arkansas": "AR",
            "california": "CA",
            "colorado": "CO",
            "connecticut": "CT",
            "delaware": "DE",
            "florida": "FL",
            "georgia": "GA",
            "hawaii": "HI",
            "idaho": "ID",
            "illinois": "IL",
            "indiana": "IN",
            "iowa": "IA",
            "kansas": "KS",
            "kentucky": "KY",
            "louisiana": "LA",
            "maine": "ME",
            "maryland": "MD",
            "massachusetts": "MA",
            "michigan": "MI",
            "minnesota": "MN",
            "mississippi": "MS",
            "missouri": "MO",
            "montana": "MT",
            "nebraska": "NE",
            "nevada": "NV",
            "new hampshire": "NH",
            "new jersey": "NJ",
            "new mexico": "NM",
            "new york": "NY",
            "north carolina": "NC",
            "north dakota": "ND",
            "ohio": "OH",
            "oklahoma": "OK",
            "oregon": "OR",
            "pennsylvania": "PA",
            "rhode island": "RI",
            "south carolina": "SC",
            "south dakota": "SD",
            "tennessee": "TN",
            "texas": "TX",
            "utah": "UT",
            "vermont": "VT",
            "virginia": "VA",
            "washington": "WA",
            "west virginia": "WV",
            "wisconsin": "WI",
            "wyoming": "WY",
        }

        def convert_state(val):
            if pd.isna(val):
                return None
            val_str = str(val).strip().lower()
            if val_str in state_map:
                return state_map[val_str]
            # If already 2 letters, uppercase it
            if len(val_str) == 2:
                return val_str.upper()
            return val_str.upper()[:2]

        return series.apply(convert_state)
