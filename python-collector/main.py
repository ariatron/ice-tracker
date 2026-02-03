"""Main entry point for ICE data collector service."""
import logging
import sys
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from config import config
from database.models import init_db
from scrapers.ohss_scraper import OHSSScraper

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"{config.LOG_DIR}/collector.log"),
    ],
)

logger = logging.getLogger(__name__)


def run_ohss_scraper():
    """Run the OHSS scraper job."""
    logger.info("=" * 80)
    logger.info("Starting OHSS scraper job")
    logger.info("=" * 80)

    try:
        scraper = OHSSScraper()
        result = scraper.scrape()

        if result["success"]:
            logger.info(f"OHSS scraper completed successfully. Records: {result['records_fetched']}")
        else:
            logger.error(f"OHSS scraper failed: {result.get('error')}")

    except Exception as e:
        logger.error(f"OHSS scraper job failed with exception: {e}", exc_info=True)

    logger.info("=" * 80)
    logger.info("OHSS scraper job finished")
    logger.info("=" * 80)


def run_trac_scraper():
    """Run the TRAC scraper job (placeholder for Phase 2)."""
    logger.info("TRAC scraper not yet implemented (Phase 2)")


def run_deportation_project_scraper():
    """Run the Deportation Data Project scraper (placeholder for Phase 2)."""
    logger.info("Deportation Data Project scraper not yet implemented (Phase 2)")


def initialize_database():
    """Initialize database connection."""
    logger.info("Initializing database connection...")
    try:
        engine = init_db()
        logger.info(f"Database connection established: {config.TIMESCALE_HOST}:{config.TIMESCALE_PORT}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        return False


def run_initial_scrape():
    """Run an initial scrape on startup."""
    logger.info("Running initial data collection on startup...")
    run_ohss_scraper()


def main():
    """Main application entry point."""
    logger.info("=" * 80)
    logger.info("ICE Data Collector Service Starting")
    logger.info(f"Timezone: {config.SCHEDULER_TIMEZONE}")
    logger.info(f"Database: {config.TIMESCALE_HOST}:{config.TIMESCALE_PORT}/{config.TIMESCALE_DATABASE}")
    logger.info(f"Scraper enabled: {config.SCRAPER_ENABLED}")
    logger.info("=" * 80)

    # Initialize database
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        sys.exit(1)

    # Check if scraping is enabled
    if not config.SCRAPER_ENABLED:
        logger.warning("Scraper is disabled. Service will not collect data.")
        logger.info("Keeping service alive for health checks...")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
            sys.exit(0)

    # Run initial scrape
    run_initial_scrape()

    # Set up scheduler
    timezone = pytz.timezone(config.SCHEDULER_TIMEZONE)
    scheduler = BlockingScheduler(timezone=timezone)

    # Schedule OHSS scraper (daily at 2 AM CST)
    scheduler.add_job(
        run_ohss_scraper,
        trigger=CronTrigger.from_crontab(config.OHSS_SCHEDULE, timezone=timezone),
        id="ohss_scraper",
        name="OHSS Data Scraper",
        replace_existing=True,
    )
    logger.info(f"Scheduled OHSS scraper: {config.OHSS_SCHEDULE}")

    # Schedule TRAC scraper (weekly on Monday at 3 AM)
    scheduler.add_job(
        run_trac_scraper,
        trigger=CronTrigger.from_crontab(config.TRAC_SCHEDULE, timezone=timezone),
        id="trac_scraper",
        name="TRAC Data Scraper",
        replace_existing=True,
    )
    logger.info(f"Scheduled TRAC scraper: {config.TRAC_SCHEDULE}")

    # Schedule Deportation Project scraper (monthly on 1st at 4 AM)
    scheduler.add_job(
        run_deportation_project_scraper,
        trigger=CronTrigger.from_crontab(config.DEPORTATION_PROJECT_SCHEDULE, timezone=timezone),
        id="deportation_project_scraper",
        name="Deportation Data Project Scraper",
        replace_existing=True,
    )
    logger.info(f"Scheduled Deportation Project scraper: {config.DEPORTATION_PROJECT_SCHEDULE}")

    # Print scheduled jobs
    logger.info("=" * 80)
    logger.info("Scheduled Jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name}: {job.id}")
    logger.info("=" * 80)

    # Start scheduler
    try:
        logger.info("Starting scheduler... Press Ctrl+C to exit")
        scheduler.start()

        # Print next run times after scheduler starts
        logger.info("=" * 80)
        logger.info("Next scheduled runs:")
        for job in scheduler.get_jobs():
            if hasattr(job, 'next_run_time') and job.next_run_time:
                logger.info(f"  - {job.name}: {job.next_run_time}")
        logger.info("=" * 80)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
