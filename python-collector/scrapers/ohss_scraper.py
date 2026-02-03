"""OHSS (DHS Office of Homeland Security Statistics) data scraper."""
import logging
import re
import os
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import config
from database.models import Arrest, Detention, Removal, DataSourceHealth, get_session

logger = logging.getLogger(__name__)


class OHSSScraper:
    """Scraper for DHS OHSS monthly enforcement data."""

    def __init__(self):
        self.base_url = config.OHSS_BASE_URL
        self.data_path = config.OHSS_DATA_PATH
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})
        self.data_dir = os.path.join(config.DATA_DIR, "ohss")
        os.makedirs(self.data_dir, exist_ok=True)

    def scrape(self) -> Dict[str, any]:
        """Main scraping method."""
        logger.info("Starting OHSS data scraping...")
        result = {
            "success": False,
            "records_fetched": 0,
            "error": None,
        }

        try:
            # Get the page with links to CSV files
            page_url = f"{self.base_url}{self.data_path}"
            logger.info(f"Fetching OHSS page: {page_url}")

            response = self.session.get(page_url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()

            # Parse the page for CSV/Excel links
            soup = BeautifulSoup(response.content, "html.parser")
            download_links = self._find_data_links(soup)

            logger.info(f"Found {len(download_links)} data files")

            # Download and process each file
            total_records = 0
            for link_info in download_links:
                try:
                    records = self._process_data_file(link_info)
                    total_records += records
                except Exception as e:
                    logger.error(f"Error processing {link_info['url']}: {e}")
                    continue

            result["success"] = True
            result["records_fetched"] = total_records
            logger.info(f"OHSS scraping completed. Total records: {total_records}")

        except Exception as e:
            logger.error(f"OHSS scraping failed: {e}")
            result["error"] = str(e)

        # Record health check
        self._record_health_check(result)

        return result

    def _find_data_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Find all data file links on the OHSS page."""
        links = []

        # Look for links to CSV, Excel files
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)

            # Check if it's a data file
            if any(ext in href.lower() for ext in [".csv", ".xlsx", ".xls"]):
                # Ensure absolute URL
                if not href.startswith("http"):
                    href = f"{self.base_url}{href}" if href.startswith("/") else f"{self.base_url}/{href}"

                # Try to extract date/month from link text or href
                month_year = self._extract_date(text) or self._extract_date(href)

                links.append(
                    {
                        "url": href,
                        "text": text,
                        "type": self._classify_data_type(text, href),
                        "date": month_year,
                    }
                )

        return links

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract month/year from text."""
        # Look for patterns like "January 2026", "Jan 2026", "2026-01", etc.
        patterns = [
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})",
            r"(\d{4})[-_](\d{2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    def _classify_data_type(self, text: str, url: str) -> str:
        """Classify the type of data file."""
        combined = f"{text} {url}".lower()

        if "arrest" in combined or "apprehension" in combined:
            return "arrests"
        elif "detention" in combined or "facility" in combined:
            return "detentions"
        elif "removal" in combined or "deportation" in combined or "return" in combined:
            return "removals"
        else:
            return "unknown"

    def _process_data_file(self, link_info: Dict[str, str]) -> int:
        """Download and process a data file."""
        url = link_info["url"]
        data_type = link_info["type"]
        logger.info(f"Processing {data_type} file: {url}")

        # Download the file
        response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()

        # Save to disk for debugging/backup
        filename = os.path.basename(url)
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)

        # Read into pandas based on file type
        if url.endswith(".csv"):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        logger.info(f"Loaded {len(df)} rows from {filename}")

        # Process based on data type
        if data_type == "arrests":
            return self._import_arrests(df, link_info)
        elif data_type == "detentions":
            return self._import_detentions(df, link_info)
        elif data_type == "removals":
            return self._import_removals(df, link_info)
        else:
            logger.warning(f"Unknown data type: {data_type}")
            return 0

    def _import_arrests(self, df: pd.DataFrame, link_info: Dict) -> int:
        """Import arrest data into database."""
        db = get_session()
        records_imported = 0

        try:
            # This is a generic import - will need to be customized based on actual CSV structure
            # For now, we'll make assumptions about column names

            # Common column name mappings
            col_mappings = {
                "state": ["state", "state_code", "st"],
                "county": ["county", "county_name"],
                "city": ["city", "city_name"],
                "arrests": ["arrests", "arrest_count", "total_arrests"],
                "criminal": ["criminal_arrests", "criminal"],
                "non_criminal": ["non_criminal_arrests", "non_criminal", "civil"],
                "date": ["date", "month", "year_month", "period"],
            }

            # Find actual column names
            cols = self._map_columns(df.columns, col_mappings)

            for _, row in df.iterrows():
                try:
                    arrest = Arrest(
                        timestamp=self._parse_timestamp(
                            row.get(cols.get("date")) if cols.get("date") else link_info.get("date")
                        ),
                        state=str(row.get(cols.get("state")))[:2] if cols.get("state") else None,
                        county=str(row.get(cols.get("county"))) if cols.get("county") else None,
                        city=str(row.get(cols.get("city"))) if cols.get("city") else None,
                        arrest_count=int(row.get(cols.get("arrests"), 0)) if cols.get("arrests") else None,
                        criminal_arrests=int(row.get(cols.get("criminal"), 0)) if cols.get("criminal") else None,
                        non_criminal_arrests=int(row.get(cols.get("non_criminal"), 0))
                        if cols.get("non_criminal")
                        else None,
                        data_source="OHSS",
                        source_url=link_info["url"],
                    )
                    db.add(arrest)
                    records_imported += 1
                except Exception as e:
                    logger.warning(f"Error importing arrest record: {e}")
                    continue

            db.commit()
            logger.info(f"Imported {records_imported} arrest records")

        except Exception as e:
            logger.error(f"Error importing arrests: {e}")
            db.rollback()
        finally:
            db.close()

        return records_imported

    def _import_detentions(self, df: pd.DataFrame, link_info: Dict) -> int:
        """Import detention data into database."""
        db = get_session()
        records_imported = 0

        try:
            col_mappings = {
                "facility": ["facility", "facility_name", "detention_facility"],
                "facility_id": ["facility_id", "id", "facility_code"],
                "state": ["state", "state_code", "st"],
                "city": ["city", "city_name"],
                "detained": ["detained", "detained_count", "population", "adp"],
                "capacity": ["capacity", "bed_capacity", "total_capacity"],
                "date": ["date", "month", "year_month", "period"],
            }

            cols = self._map_columns(df.columns, col_mappings)

            for _, row in df.iterrows():
                try:
                    detention = Detention(
                        timestamp=self._parse_timestamp(
                            row.get(cols.get("date")) if cols.get("date") else link_info.get("date")
                        ),
                        facility_name=str(row.get(cols.get("facility"))) if cols.get("facility") else None,
                        facility_id=str(row.get(cols.get("facility_id"))) if cols.get("facility_id") else None,
                        state=str(row.get(cols.get("state")))[:2] if cols.get("state") else None,
                        city=str(row.get(cols.get("city"))) if cols.get("city") else None,
                        detained_count=int(row.get(cols.get("detained"), 0)) if cols.get("detained") else None,
                        capacity=int(row.get(cols.get("capacity"), 0)) if cols.get("capacity") else None,
                        data_source="OHSS",
                    )
                    db.add(detention)
                    records_imported += 1
                except Exception as e:
                    logger.warning(f"Error importing detention record: {e}")
                    continue

            db.commit()
            logger.info(f"Imported {records_imported} detention records")

        except Exception as e:
            logger.error(f"Error importing detentions: {e}")
            db.rollback()
        finally:
            db.close()

        return records_imported

    def _import_removals(self, df: pd.DataFrame, link_info: Dict) -> int:
        """Import removal/deportation data into database."""
        db = get_session()
        records_imported = 0

        try:
            col_mappings = {
                "state": ["state", "state_code", "st"],
                "removals": ["removals", "removal_count", "deportations"],
                "country": ["country", "country_of_citizenship", "nationality"],
                "type": ["removal_type", "type", "category"],
                "date": ["date", "month", "year_month", "period"],
            }

            cols = self._map_columns(df.columns, col_mappings)

            for _, row in df.iterrows():
                try:
                    removal = Removal(
                        timestamp=self._parse_timestamp(
                            row.get(cols.get("date")) if cols.get("date") else link_info.get("date")
                        ),
                        state=str(row.get(cols.get("state")))[:2] if cols.get("state") else None,
                        removal_count=int(row.get(cols.get("removals"), 0)) if cols.get("removals") else None,
                        country_of_citizenship=str(row.get(cols.get("country"))) if cols.get("country") else None,
                        removal_type=str(row.get(cols.get("type"))) if cols.get("type") else "removal",
                        data_source="OHSS",
                    )
                    db.add(removal)
                    records_imported += 1
                except Exception as e:
                    logger.warning(f"Error importing removal record: {e}")
                    continue

            db.commit()
            logger.info(f"Imported {records_imported} removal records")

        except Exception as e:
            logger.error(f"Error importing removals: {e}")
            db.rollback()
        finally:
            db.close()

        return records_imported

    def _map_columns(self, actual_cols: List[str], mappings: Dict) -> Dict[str, str]:
        """Map actual CSV columns to expected column names."""
        result = {}
        actual_cols_lower = [col.lower().strip() for col in actual_cols]

        for key, possible_names in mappings.items():
            for name in possible_names:
                if name.lower() in actual_cols_lower:
                    idx = actual_cols_lower.index(name.lower())
                    result[key] = actual_cols[idx]
                    break

        return result

    def _parse_timestamp(self, date_str: any) -> datetime:
        """Parse various date formats into a timestamp."""
        if pd.isna(date_str) or date_str is None:
            return datetime.now()

        date_str = str(date_str).strip()

        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
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

        # Default to first of current month if parsing fails
        logger.warning(f"Could not parse date: {date_str}, using current date")
        return datetime.now().replace(day=1)

    def _record_health_check(self, result: Dict):
        """Record health check result."""
        db = get_session()
        try:
            health = DataSourceHealth(
                source_name="OHSS",
                last_attempt=datetime.now(),
                last_successful_fetch=datetime.now() if result["success"] else None,
                status="success" if result["success"] else "failed",
                error_message=result.get("error"),
                records_fetched=result.get("records_fetched", 0),
            )
            db.add(health)
            db.commit()
        except Exception as e:
            logger.error(f"Error recording health check: {e}")
            db.rollback()
        finally:
            db.close()
