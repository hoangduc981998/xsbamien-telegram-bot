# 🔄 Lô Gan Refactor: Draws-Based Analysis

## 📋 Summary

This refactor changes the Lô Gan calculation from using **"days" (calendar days)** to **"draws" (draw periods)** as the primary parameter, making the feature province-agnostic and more intuitive.

## 🎯 Problem Solved

### Before (days=200):
```python
# Same "days" meant different things for different provinces:
gan_data = await service.get_lo_gan('ANGI', days=200)
# ANGI (1 draw/week): 200 days = ~29 draws
# Missing: số 98 (59 kỳ), số 02 (29 kỳ)

gan_data = await service.get_lo_gan('TPHCM', days=200)
# TPHCM (2 draws/week): 200 days = ~58 draws

gan_data = await service.get_lo_gan('MB', days=200)
# MB (7 draws/week): 200 days = 200 draws
```

**Issue:** Inconsistent meaning across provinces, confusing for users.

### After (draws=200):
```python
# Same "draws" means same thing for ALL provinces:
gan_data = await service.get_lo_gan('ANGI', draws=200)
# ANGI: 200 draws ≈ 1407 days
# Includes: số 98 (59 kỳ) ✅, số 02 (29 kỳ) ✅

gan_data = await service.get_lo_gan('TPHCM', draws=200)
# TPHCM: 200 draws ≈ 707 days

gan_data = await service.get_lo_gan('MB', draws=200)
# MB: 200 draws = 200 days
```

**Solution:** Province-agnostic, intuitive, consistent.

## 📝 Changes Made

### 1. statistics_db_service.py
```python
async def get_lo_gan(
    self,
    province_code: str,
    draws: int | None = None,  # NEW! Primary parameter
    days: int | None = None,   # Keep for backward compatibility
    limit: int = 15
) -> list:
```

**Key logic:**
- If `draws` specified: Calculate calendar days based on province schedule
- If `days` specified: Use directly (backward compat, with deprecation warning)
- If neither: Default to 200 draws
- Add metadata to results: `analysis_draws`, `analysis_days`, `analysis_window`

### 2. statistics_service.py
```python
async def get_lo_gan(
    self, 
    province_code: str, 
    draws: int = 200,  # NEW! Default to 200 draws
    limit: int = 10
) -> List[Dict]:
```

### 3. callbacks.py
```python
# Before:
gan_data = await statistics_service.get_lo_gan(province_key, days=200, limit=15)

# After:
gan_data = await statistics_service.get_lo_gan(province_key, draws=200, limit=15)
```

### 4. formatters.py
```python
def format_lo_gan(gan_data: list, province_name: str) -> str:
    # Get metadata from first item
    analysis_draws = gan_data[0].get('analysis_draws')
    analysis_days = gan_data[0].get('analysis_days')
    is_daily = gan_data[0].get('is_daily', False)
    
    # Determine display text
    if analysis_draws:
        unit = "ngày" if is_daily else "kỳ"
        window_text = f"{analysis_draws} {unit} quay gần nhất"
    else:
        window_text = f"{analysis_days} ngày (chỉ số đã từng về)"
```

## 🧮 Draw Calculation Logic

```python
def calculate_days_from_draws(province_code: str, draws: int) -> int:
    """Calculate calendar days from draws"""
    is_daily = is_daily_draw_province(province_code)
    
    if is_daily:
        # MB: 1 draw per day
        return draws
    else:
        # MN/MT: Get draw frequency from schedule
        schedule = PROVINCE_DRAW_SCHEDULE.get(province_code, [3])
        draws_per_week = len(schedule)
        
        # Calculate days needed to cover 'draws' periods
        # Add buffer to ensure we get enough data
        return int((draws / draws_per_week) * 7) + 7
```

## 📊 Examples

### An Giang (1 draw/week - Thursday)
```python
draws = 200
days = int((200 / 1) * 7) + 7 = 1407 days
# 200 draws = ~200 weeks = ~1407 days
```

### TP.HCM (2 draws/week - Monday, Saturday)
```python
draws = 200
days = int((200 / 2) * 7) + 7 = 707 days
# 200 draws = ~100 weeks = ~707 days
```

### Miền Bắc (7 draws/week - daily)
```python
draws = 200
days = 200
# 200 draws = 200 days (1:1)
```

## 🎨 Display Output

### An Giang (periodic draws)
```
📊 LÔ GAN AN GIANG
📅 Phân tích 200 kỳ quay gần nhất

🔢 Top 15 Lô Gan Dài Nhất:
━━━━━━━━━━━━━━━━━━━━
🔴  1. 98 - 59 kỳ
     └ Lần cuối: 01/08/2025
     └ Gan max: 65 kỳ
```

### Miền Bắc (daily draws)
```
📊 LÔ GAN MIỀN BẮC
📅 Phân tích 200 ngày quay gần nhất

🔢 Top 15 Lô Gan Dài Nhất:
━━━━━━━━━━━━━━━━━━━━
🔴  1. 45 - 25 ngày
     └ Lần cuối: 20/09/2025
     └ Gan max: 30 ngày
```

## ✅ Backward Compatibility

The old `days` parameter still works:
```python
# Old API (deprecated, but still works)
await service.get_lo_gan('ANGI', days=1400)
# Warning logged: "Using deprecated 'days' parameter"

# New API (recommended)
await service.get_lo_gan('ANGI', draws=200)
```

## 🧪 Testing

### Test Coverage
- ✅ 35 tests for lo_gan functionality
- ✅ 127 total tests passing
- ✅ Draw calculation logic
- ✅ Metadata structure
- ✅ Display formatting
- ✅ Backward compatibility
- ✅ Province-agnostic behavior
- ✅ Real-world scenarios

### Test Files
1. `tests/test_draws_refactor.py` - Unit tests for draws logic
2. `tests/test_draws_integration.py` - Integration tests
3. `tests/test_lo_gan_fixes.py` - Updated existing tests
4. `tests/manual_verify_draws.py` - Manual verification script

## 🚀 Benefits

1. **Province-Agnostic**: Same number means same thing across all provinces
2. **Intuitive**: "200 draws" = 200 lottery drawing events
3. **Consistent**: No more confusion about different meanings
4. **Backward Compatible**: Old code still works
5. **Better Coverage**: Larger analysis window finds more patterns
6. **Clear Display**: Shows correct unit (kỳ/ngày) automatically

## 📈 Impact

### ANGI Example
- **Before**: days=200 → Missing số 98 (59 kỳ) and 02 (29 kỳ)
- **After**: draws=200 → Includes both số 98 and 02 ✅

### Window Size Comparison
| Province | draws=200 | Equivalent Days | Before (days=200) |
|----------|-----------|-----------------|-------------------|
| MB       | 200 draws | 200 days        | 200 days (same)   |
| ANGI     | 200 draws | 1407 days       | 200 days (~7x)    |
| TPHCM    | 200 draws | 707 days        | 200 days (~3.5x)  |

## 🔍 Verification

Run the manual verification script:
```bash
python tests/manual_verify_draws.py
```

Run all tests:
```bash
pytest tests/test_lo_gan_fixes.py tests/test_draws_refactor.py tests/test_draws_integration.py -v
```

## 📚 API Reference

### get_lo_gan (statistics_db_service.py)
```python
async def get_lo_gan(
    self,
    province_code: str,
    draws: int | None = None,
    days: int | None = None,
    limit: int = 15
) -> list[dict]
```

**Parameters:**
- `province_code`: Province code (e.g., 'ANGI', 'TPHCM', 'MB')
- `draws`: Number of recent draw periods to analyze (recommended)
- `days`: Number of calendar days (deprecated, use draws instead)
- `limit`: Maximum number of results (default: 15)

**Returns:**
List of dicts with:
- `number`: 2-digit lottery number
- `gan_value`: Primary display value (days or periods)
- `days_since_last`: Days since last appearance
- `periods_since_last`: Periods since last appearance
- `last_seen_date`: Date of last appearance (DD/MM/YYYY)
- `max_cycle`: Maximum gap in history
- `is_daily`: Whether province draws daily
- `category`: "cuc_gan", "gan_lon", or "gan_thuong"
- `analysis_draws`: Number of draws analyzed (or None)
- `analysis_days`: Number of days analyzed
- `analysis_window`: Display text for window size

## 🎓 Migration Guide

### For Users
Just use the bot - the display will automatically show the correct unit!

### For Developers
```python
# Old code (still works, but deprecated)
gan_data = await service.get_lo_gan('ANGI', days=200)

# New code (recommended)
gan_data = await service.get_lo_gan('ANGI', draws=200)

# Access metadata
if gan_data:
    item = gan_data[0]
    print(f"Window: {item['analysis_window']}")
    print(f"Draws: {item['analysis_draws']}")
    print(f"Days: {item['analysis_days']}")
```

## 📞 Questions?

See the test files for examples:
- `tests/test_draws_refactor.py` - Comprehensive unit tests
- `tests/test_draws_integration.py` - Integration examples
- `tests/manual_verify_draws.py` - Manual verification

---

**Status**: ✅ Fully Implemented and Tested
**Date**: October 2025
**Priority**: HIGH
**Impact**: All MN/MT provinces benefit from larger analysis window
