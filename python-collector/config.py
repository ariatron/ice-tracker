"""Configuration management for ICE data collector."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Database settings
    TIMESCALE_HOST = os.getenv("TIMESCALE_HOST", "localhost")
    TIMESCALE_PORT = int(os.getenv("TIMESCALE_PORT", "5432"))
    TIMESCALE_USER = os.getenv("TIMESCALE_USER", "ice_tracker")
    TIMESCALE_PASSWORD = os.getenv("TIMESCALE_PASSWORD", "")
    TIMESCALE_DATABASE = os.getenv("TIMESCALE_DATABASE", "ice_activities")

    @property
    def DATABASE_URL(self):
        """Build PostgreSQL connection URL."""
        return (
            f"postgresql://{self.TIMESCALE_USER}:{self.TIMESCALE_PASSWORD}"
            f"@{self.TIMESCALE_HOST}:{self.TIMESCALE_PORT}/{self.TIMESCALE_DATABASE}"
        )

    # Scheduler settings
    SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "America/Chicago")
    SCRAPER_ENABLED = os.getenv("SCRAPER_ENABLED", "true").lower() == "true"

    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", "/logs")

    # Data storage
    DATA_DIR = os.getenv("DATA_DIR", "/data")

    # Scraper settings
    USER_AGENT = "ICE Activities Tracker (Research/Monitoring Project)"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3

    # OHSS specific settings
    OHSS_BASE_URL = "https://ohss.dhs.gov"
    OHSS_DATA_PATH = "/topics/immigration/immigration-enforcement/monthly-tables"

    # Schedule times (cron format)
    OHSS_SCHEDULE = "0 2 * * *"  # Daily at 2 AM CST
    TRAC_SCHEDULE = "0 3 * * 1"  # Weekly on Monday at 3 AM
    DEPORTATION_PROJECT_SCHEDULE = "0 4 1 * *"  # Monthly on 1st at 4 AM


config = Config()
