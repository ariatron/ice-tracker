"""Data normalization utilities."""
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalize data from different sources into consistent formats."""

    @staticmethod
    def normalize_timestamp(date_value: any, default: Optional[datetime] = None) -> Optional[datetime]:
        """Normalize various date formats into a datetime object."""
        if date_value is None:
            return default or datetime.now()

        if isinstance(date_value, datetime):
            return date_value

        # Try to parse string dates
        date_str = str(date_value).strip()

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m",
            "%B %Y",
            "%b %Y",
            "%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse date: {date_value}")
        return default or datetime.now()

    @staticmethod
    def normalize_state_code(state_value: any) -> Optional[str]:
        """Normalize state values to 2-letter codes."""
        if state_value is None:
            return None

        state_str = str(state_value).strip().upper()

        # If already 2 characters, return as-is
        if len(state_str) == 2:
            return state_str

        # Map common state names
        state_names = {
            "ALABAMA": "AL",
            "ALASKA": "AK",
            "ARIZONA": "AZ",
            "ARKANSAS": "AR",
            "CALIFORNIA": "CA",
            "COLORADO": "CO",
            "CONNECTICUT": "CT",
            "DELAWARE": "DE",
            "FLORIDA": "FL",
            "GEORGIA": "GA",
            "HAWAII": "HI",
            "IDAHO": "ID",
            "ILLINOIS": "IL",
            "INDIANA": "IN",
            "IOWA": "IA",
            "KANSAS": "KS",
            "KENTUCKY": "KY",
            "LOUISIANA": "LA",
            "MAINE": "ME",
            "MARYLAND": "MD",
            "MASSACHUSETTS": "MA",
            "MICHIGAN": "MI",
            "MINNESOTA": "MN",
            "MISSISSIPPI": "MS",
            "MISSOURI": "MO",
            "MONTANA": "MT",
            "NEBRASKA": "NE",
            "NEVADA": "NV",
            "NEW HAMPSHIRE": "NH",
            "NEW JERSEY": "NJ",
            "NEW MEXICO": "NM",
            "NEW YORK": "NY",
            "NORTH CAROLINA": "NC",
            "NORTH DAKOTA": "ND",
            "OHIO": "OH",
            "OKLAHOMA": "OK",
            "OREGON": "OR",
            "PENNSYLVANIA": "PA",
            "RHODE ISLAND": "RI",
            "SOUTH CAROLINA": "SC",
            "SOUTH DAKOTA": "SD",
            "TENNESSEE": "TN",
            "TEXAS": "TX",
            "UTAH": "UT",
            "VERMONT": "VT",
            "VIRGINIA": "VA",
            "WASHINGTON": "WA",
            "WEST VIRGINIA": "WV",
            "WISCONSIN": "WI",
            "WYOMING": "WY",
        }

        return state_names.get(state_str, state_str[:2] if state_str else None)

    @staticmethod
    def clean_numeric(value: any, default: int = 0) -> int:
        """Clean and convert numeric values."""
        if value is None:
            return default

        try:
            # Remove commas, dollar signs, etc.
            if isinstance(value, str):
                value = value.replace(",", "").replace("$", "").strip()

            return int(float(value))
        except (ValueError, TypeError):
            logger.warning(f"Could not convert to numeric: {value}")
            return default

    @staticmethod
    def deduplicate_key(source: str, timestamp: datetime, location: dict) -> str:
        """Generate a deduplication key for a record."""
        # Create a hash key from source, timestamp, and location
        location_str = f"{location.get('state', '')}_{location.get('city', '')}_{location.get('county', '')}"
        timestamp_str = timestamp.strftime("%Y-%m-%d") if isinstance(timestamp, datetime) else str(timestamp)
        return f"{source}_{timestamp_str}_{location_str}".lower().replace(" ", "_")

    @staticmethod
    def validate_latitude(lat: any) -> Optional[float]:
        """Validate and normalize latitude values."""
        try:
            lat_float = float(lat)
            if -90 <= lat_float <= 90:
                return lat_float
            logger.warning(f"Invalid latitude: {lat}")
            return None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_longitude(lon: any) -> Optional[float]:
        """Validate and normalize longitude values."""
        try:
            lon_float = float(lon)
            if -180 <= lon_float <= 180:
                return lon_float
            logger.warning(f"Invalid longitude: {lon}")
            return None
        except (ValueError, TypeError):
            return None
