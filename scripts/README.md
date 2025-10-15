# Database Management Scripts

This directory contains utility scripts for managing the lottery database.

## Available Scripts

### load_historical_data.py

Load historical lottery data from MU88 API into the database.

**Usage:**

```bash
# Load 100 days for all provinces
python scripts/load_historical_data.py --days 100 --all

# Load for specific province
python scripts/load_historical_data.py --days 60 --province MB

# Load for a region
python scripts/load_historical_data.py --days 30 --region MN

# Initialize database and load data
python scripts/load_historical_data.py --init-db --days 100 --all
```

**Options:**
- `--days N`: Number of days to load (default: 100)
- `--all`: Load all provinces (36 provinces)
- `--province CODE`: Load specific province (MB, TPHCM, etc.)
- `--region CODE`: Load region (MB, MN, MT)
- `--skip-existing`: Skip provinces with existing data (default: true)
- `--delay N`: Delay between API calls (default: 1.0 seconds)
- `--init-db`: Initialize database tables first

**Examples:**

```bash
# First time setup
python scripts/load_historical_data.py --init-db --days 100 --all --delay 1.5

# Update daily
python scripts/load_historical_data.py --days 1 --all --skip-existing false

# Load missing province
python scripts/load_historical_data.py --days 100 --province DANA

# Quick test with one region
python scripts/load_historical_data.py --days 10 --region MB
```

## Requirements

- PostgreSQL database running
- Database credentials in `.env` file
- Internet connection for MU88 API access

## Troubleshooting

**Database connection error:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U lottery_user -d lottery_db
```

**API rate limiting:**
Increase `--delay` parameter:
```bash
python scripts/load_historical_data.py --days 100 --all --delay 2.0
```

**Permission errors:**
Make sure script is executable:
```bash
chmod +x scripts/load_historical_data.py
```

## Development

To add new scripts:

1. Create new Python file in `scripts/` directory
2. Add `#!/usr/bin/env python3` shebang
3. Import required modules from `app/`
4. Document usage in this README

## Support

For issues or questions:
- Check `docs/DATABASE.md` for database setup
- Review logs in console output
- Contact: @hoangduc981998
