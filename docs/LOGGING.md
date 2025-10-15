# 📊 Logging System Documentation

## Overview

Bot sử dụng comprehensive logging system để monitor, debug, và audit operations.

## Log Files

### Vị trí

### Log Rotation
- **app.log, error.log:** Max 10MB, keep 5 backups
- **cache.log:** Max 5MB, keep 3 backups
- Auto compression: Enabled

## Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Development details | Cache hit/miss, conversion formula |
| INFO | Normal operations | Cache refresh, keyboard generation |
| WARNING | Warnings | Cache cleared manually |
| ERROR | Errors | Exception caught, API errors |
| CRITICAL | Critical failures | System crash |

## Log Format


**Example:**

## Common Log Messages

### Cache Operations

**Cache Refresh:**

**Cache Hit:**

**Cache Miss:**


**Cache Cleared:**

## Monitoring

### Check Cache Stats

```python
from app.utils.cache import ScheduleCache

info = ScheduleCache.get_cache_info()
print(f"Cache hits: {info['stats']['cache_hits']}")
print(f"Hit rate: {info['stats']['hit_rate']:.1f}%")

# All logs
tail -f logs/app.log

# Errors only
tail -f logs/error.log

# Cache only
tail -f logs/cache.log

# Last 100 lines
tail -n 100 logs/app.log

# Find cache refresh events
grep "Cache refreshed" logs/cache.log

# Find errors
grep "ERROR" logs/app.log

# Find specific date
grep "2025-10-15" logs/app.log

# Count cache hits
grep "Cache HIT" logs/cache.log | wc -l
Troubleshooting
High Cache Miss Rate
If cache miss rate > 10%:

Check if bot is restarting frequently
Verify timezone is UTC
Check for clock skew
No Logs Generated
If logs are not being created:

Verify logs/ directory exists
Check file permissions
Ensure logging is initialized
Log Files Too Large
If log files grow too fast:

Increase log rotation size in logging_config.py
Reduce log level from DEBUG to INFO
Archive old logs manually
Best Practices
Production: Use INFO level for console, DEBUG for files
Development: Use DEBUG level for everything
Monitor: Check error.log regularly
Archive: Backup and compress old logs monthly
Analyze: Use log analysis tools for patterns
Integration with Monitoring Tools


# Forward logs to Logstash
filebeat -e -c filebeat.yml
# Monitor logs directory
splunk add monitor logs/
# Stream logs to CloudWatch
aws logs create-log-group --log-group-name xsbamien-bot

### Bước 3: Paste vào nano

Trong màn hình nano (màu xanh):
1. **Chuột phải** → chọn Paste
2. Hoặc **Shift + Insert**
3. Hoặc **Ctrl + Shift + V**

### Bước 4: Save file

1. Nhấn **Ctrl + O** (chữ O, không phải số 0)
2. Sẽ thấy dòng: `File Name to Write: docs/LOGGING.md`
3. Nhấn **Enter**
4. Nhấn **Ctrl + X** để thoát

---

## ✅ Verify file đã tạo thành công

```bash
# Kiểm tra file
ls -lh docs/LOGGING.md

# Xem 10 dòng đầu
head -n 10 docs/LOGGING.md

