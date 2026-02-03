"""SQLAlchemy database models for ICE activities tracking."""
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Numeric,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config

Base = declarative_base()


class Arrest(Base):
    """Arrest activities table."""

    __tablename__ = "arrests"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    state = Column(String(2))
    county = Column(String(100))
    city = Column(String(100))
    arrest_count = Column(Integer)
    criminal_arrests = Column(Integer)
    non_criminal_arrests = Column(Integer)
    data_source = Column(String(50))
    source_url = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Detention(Base):
    """Detention facilities table."""

    __tablename__ = "detentions"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    facility_name = Column(String(255))
    facility_id = Column(String(50))
    state = Column(String(2))
    city = Column(String(100))
    detained_count = Column(Integer)
    capacity = Column(Integer)
    avg_daily_population = Column(Numeric(10, 2))
    facility_type = Column(String(50))
    data_source = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Removal(Base):
    """Removals and deportations table."""

    __tablename__ = "removals"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    state = Column(String(2))
    removal_count = Column(Integer)
    country_of_citizenship = Column(String(100))
    removal_type = Column(String(50))
    data_source = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class CommunityReport(Base):
    """Community-reported ICE activities."""

    __tablename__ = "community_reports"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    report_type = Column(String(50))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    state = Column(String(2))
    city = Column(String(100))
    address = Column(Text)
    description = Column(Text)
    verified = Column(Boolean, default=False)
    data_source = Column(String(50))
    source_url = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class NewsArticle(Base):
    """News articles about ICE activities."""

    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    title = Column(Text)
    description = Column(Text)
    url = Column(Text, unique=True)
    source = Column(String(100))
    state = Column(String(2))
    city = Column(String(100))
    sentiment = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class DataSourceHealth(Base):
    """Data source health monitoring."""

    __tablename__ = "data_source_health"

    id = Column(Integer, primary_key=True)
    source_name = Column(String(100))
    last_successful_fetch = Column(DateTime(timezone=True))
    last_attempt = Column(DateTime(timezone=True))
    status = Column(String(20))
    error_message = Column(Text)
    records_fetched = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# Database connection setup
engine = None
SessionLocal = None


def init_db():
    """Initialize database connection."""
    global engine, SessionLocal
    engine = create_engine(
        config.DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


def get_session():
    """Get a database session."""
    if SessionLocal is None:
        init_db()
    return SessionLocal()
