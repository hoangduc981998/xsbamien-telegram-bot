# Database Infrastructure Documentation

## Overview

This document describes the PostgreSQL database infrastructure for storing historical lottery results and enabling real-time statistics (Lô Gan, Frequency Analysis, Hot/Cold numbers).

## Architecture

### Technology Stack
- **Database**: PostgreSQL 13+
- **ORM**: SQLAlchemy 2.0 (async)
- **Driver**: asyncpg
- **Migrations**: Alembic
- **Connection Pooling**: Built-in SQLAlchemy async pool

### Design Principles
1. **Legitimate Data Source**: All data comes from MU88 API (NOT web scraping)
2. **Optimized for Statistics**: Denormalized tables for fast queries
3. **Async First**: All operations use async/await pattern
4. **Scalable**: Indexed for queries on 100+ days of data

## Database Schema

### Table: `lottery_results`

Stores complete lottery results for each province and date.

```sql
CREATE TABLE lottery_results (
    id SERIAL PRIMARY KEY,
    province_code VARCHAR(20) NOT NULL,
    province_name VARCHAR(100) NOT NULL,
    region VARCHAR(10) NOT NULL,  -- MB, MN, MT
    draw_date DATE NOT NULL,
    prizes JSON NOT NULL,  -- {"DB": ["12345"], "G1": ["67890"], ...}
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    
    UNIQUE(province_code, draw_date)
);

-- Indexes
CREATE INDEX idx_province_date ON lottery_results(province_code, draw_date);
CREATE INDEX idx_region_date ON lottery_results(region, draw_date);
CREATE INDEX idx_draw_date_desc ON lottery_results(draw_date DESC);
```

**Purpose**: Primary storage for lottery results
**Size**: ~1 KB per record, ~3.6 MB for 100 days × 36 provinces

### Table: `lo_2_so_history`

Stores extracted 2-digit numbers for fast statistics queries.

```sql
CREATE TABLE lo_2_so_history (
    id SERIAL PRIMARY KEY,
    lottery_result_id INTEGER NOT NULL,
    province_code VARCHAR(20) NOT NULL,
    region VARCHAR(10) NOT NULL,
    draw_date DATE NOT NULL,
    number VARCHAR(2) NOT NULL,  -- 00-99
    prize_type VARCHAR(10) NOT NULL,  -- DB, G1, G2, etc.
    position VARCHAR(20) NOT NULL DEFAULT 'last_2',
    created_at TIMESTAMP NOT NULL
);

-- Indexes for fast statistics queries
CREATE INDEX idx_number_date ON lo_2_so_history(number, draw_date DESC);
CREATE INDEX idx_province_number_date ON lo_2_so_history(province_code, number, draw_date);
CREATE INDEX idx_region_number_date ON lo_2_so_history(region, number, draw_date);
CREATE INDEX idx_draw_date_number ON lo_2_so_history(draw_date DESC, number);
```

**Purpose**: Denormalized table for fast frequency and Lô Gan queries
**Size**: ~100 bytes per record, ~18 MB for 100 days × 36 provinces × 27 numbers/draw

## Setup Instructions

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Docker:**
```bash
docker run --name lottery-postgres \
  -e POSTGRES_PASSWORD=lottery_pass \
  -e POSTGRES_USER=lottery_user \
  -e POSTGRES_DB=lottery_db \
  -p 5432:5432 \
  -d postgres:15-alpine
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE lottery_db;
CREATE USER lottery_user WITH PASSWORD 'lottery_pass';
GRANT ALL PRIVILEGES ON DATABASE lottery_db TO lottery_user;
\q
```

### 3. Configure Environment

Create or update `.env` file:

```bash
DATABASE_URL=postgresql+asyncpg://lottery_user:lottery_pass@localhost:5432/lottery_db
DB_ECHO=false  # Set to true for SQL query logging
```

### 4. Run Migrations

```bash
# Initialize database tables
python -m alembic upgrade head
```

### 5. Load Historical Data

**Load 100 days for all provinces:**
```bash
python scripts/load_historical_data.py --days 100 --all
```

**Load for specific province:**
```bash
python scripts/load_historical_data.py --days 100 --province MB
```

**Load for a region:**
```bash
python scripts/load_historical_data.py --days 60 --region MN
```

**Options:**
- `--days N`: Number of days to load (default: 100)
- `--all`: Load all provinces
- `--province CODE`: Load specific province
- `--region CODE`: Load region (MB, MN, MT)
- `--skip-existing`: Skip provinces with existing data (default: true)
- `--delay N`: Delay between API calls in seconds (default: 1.0)
- `--init-db`: Initialize database tables first

## Usage Examples

### Python API

#### Save Lottery Result

```python
from app.services.db import LotteryDBService

db_service = LotteryDBService()

result_data = {
    "province_code": "MB",
    "province_name": "Miền Bắc",
    "region": "MB",
    "date": "2025-10-15",
    "prizes": {
        "DB": ["12345"],
        "G1": ["67890"],
        "G2": ["11111", "22222"],
        # ...
    }
}

saved = await db_service.save_result(result_data)
print(f"Saved: {saved.id}")
```

#### Get Historical Data

```python
# Get latest result
latest = await db_service.get_latest_result("MB")

# Get last 60 days
history = await db_service.get_history("MB", limit=60)

# Get date range info
date_range = await db_service.get_date_range("MB")
# Returns: {"min_date": date(2025, 7, 7), "max_date": date(2025, 10, 15), "days": 101}
```

#### Statistics Queries

```python
from app.services.db import StatisticsDBService

stats_service = StatisticsDBService()

# Get frequency of 2-digit numbers (last 30 days)
frequency = await stats_service.get_lo2so_frequency("MB", days=30)
# Returns: {"45": 15, "12": 10, "78": 8, ...}

# Get Lô Gan (cold numbers)
lo_gan = await stats_service.get_lo_gan("MB", days=30, limit=10)
# Returns: [{"number": "00", "days_since_last": 25, "last_seen_date": "2025-09-20"}, ...]

# Get hot numbers
hot = await stats_service.get_hot_numbers("MB", days=30, limit=10)
# Returns: [{"number": "45", "count": 15}, {"number": "12", "count": 10}, ...]

# Get number history
history = await stats_service.get_number_history("MB", "45", limit=20)
# Returns: [{"date": "2025-10-15", "prize_type": "G7"}, ...]
```

### Crawler Usage

```python
from app.services.crawler import HistoricalDataCrawler

crawler = HistoricalDataCrawler()

# Crawl single province
result = await crawler.crawl_province("MB", limit=100)

# Crawl all provinces
result = await crawler.crawl_all_provinces(limit=100, delay=1.0)

# Crawl region
result = await crawler.crawl_region("MN", limit=100, delay=1.0)

# Update latest results
result = await crawler.update_latest(["MB", "TPHCM"])
```

## Performance Considerations

### Query Optimization

1. **Use Indexes**: All frequent queries use indexed columns
2. **Limit Results**: Always use `LIMIT` for large result sets
3. **Connection Pooling**: Configured for 10 connections, max 20 overflow
4. **Async Operations**: All DB operations are async for non-blocking I/O

### Typical Query Times (100 days data)

- Get latest result: ~5ms
- Get 60-day history: ~15ms
- Frequency analysis (30 days): ~20ms
- Lô Gan calculation: ~50ms
- Statistics summary: ~100ms

### Scaling Recommendations

For production with high traffic:

1. **Read Replicas**: Add read replicas for statistics queries
2. **Redis Cache**: Cache frequent queries (frequency, hot numbers)
3. **Materialized Views**: Pre-compute common statistics
4. **Partitioning**: Partition by date for very large datasets

## Maintenance

### Backup Database

```bash
# Backup
pg_dump -U lottery_user lottery_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U lottery_user lottery_db < backup_20251015.sql
```

### Update Historical Data

Run daily to keep data fresh:

```bash
python scripts/load_historical_data.py --all --days 1 --skip-existing false
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Troubleshooting

### Connection Issues

**Error**: `OSError: Multiple exceptions: [Errno 111] Connect call failed`

**Solution**: Check PostgreSQL is running:
```bash
sudo systemctl status postgresql
# or
brew services list
```

### Permission Issues

**Error**: `permission denied for table lottery_results`

**Solution**: Grant permissions:
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lottery_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO lottery_user;
```

### Migration Issues

**Error**: `Target database is not up to date`

**Solution**: 
```bash
alembic stamp head  # Mark current state
alembic upgrade head  # Apply migrations
```

## Future Enhancements

1. **Lo 3 So History**: Add table for 3-digit numbers
2. **User Preferences**: Track user favorite numbers
3. **Prediction Patterns**: Store pattern analysis results
4. **Export Feature**: Export statistics to CSV/Excel
5. **Real-time Updates**: WebSocket for live draw updates

## Support

For issues or questions:
- Check logs in `app.log`
- Review migration history: `alembic history`
- Contact: @hoangduc981998

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-15  
**Status**: ✅ Production Ready
