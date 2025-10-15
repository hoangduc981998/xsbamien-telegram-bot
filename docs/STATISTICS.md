# Statistics Features

This document describes the lottery statistics and analysis features implemented in the xsbamien-telegram-bot.

## Overview

The statistics module provides comprehensive analysis of Vietnamese lottery numbers ("Lô Đề"), helping users identify patterns and trends in lottery results.

## Features

### 📊 Lô 2 Số (2-Digit Analysis)

**Purpose**: Analyze 2-digit lottery numbers across all prize levels.

**How it works**:
- Extracts the last 2 digits from all prizes (DB, G1-G8)
- Shows all unique 2-digit numbers that appeared
- Calculates frequency of appearance
- Groups numbers by tens digit (Đầu Lô)
- Groups numbers by units digit (Đuôi Lô)

**Data source**: Current day results from API or mock data

**Usage**:
1. Select region (Miền Bắc/Miền Nam/Miền Trung) or specific province
2. Tap "📊 Thống kê Lô 2 số"
3. View analysis of today's results

**Example output**:
```
📊 THỐNG KÊ LÔ 2 SỐ - TP.HCM
📅 Ngày: 15/10/2025

🎯 Các con số đã về:
12, 23, 34, 45, 56, 67, 78, 89

📈 Tần suất xuất hiện:
• 45: 3 lần
• 23: 2 lần
• 12: 1 lần
```

### 📊 Lô 3 Số (3-Digit Analysis / Ba Càng)

**Purpose**: Analyze 3-digit lottery numbers (higher prize, lower probability).

**How it works**:
- Extracts the last 3 digits from all prizes
- Shows all unique 3-digit numbers
- Calculates frequency of appearance

**Data source**: Current day results from API or mock data

**Usage**:
1. Select a specific province
2. Tap "📊 Thống kê Lô 3 số"
3. View analysis of today's results

**Example output**:
```
📊 THỐNG KÊ LÔ 3 SỐ (BA CÀNG) - TP.HCM
📅 Ngày: 15/10/2025

🎯 Các bộ 3 số đã về:
123, 456, 789

📈 Tần suất xuất hiện:
• 456: 2 lần
• 123: 1 lần
```

### 📈 Đầu Lô / Đuôi Lô (Head/Tail Statistics)

**Purpose**: Statistical analysis of lottery numbers grouped by their first or last digit.

**How it works**:

**Đầu Lô (Head numbers)**:
- Groups all 2-digit numbers by their tens digit (0-9)
- Shows which units digits appear with each tens digit

**Đuôi Lô (Tail numbers)**:
- Groups all 2-digit numbers by their units digit (0-9)
- Shows which tens digits appear with each units digit

**Data source**: Current day results (typically for Miền Bắc)

**Usage**:
1. Navigate to Statistics menu
2. Tap "📈 Đầu-Đuôi ĐB"
3. View grouped analysis

**Example output**:
```
📊 THỐNG KÊ ĐẦU LÔ
🔢 0 : 1, 5, 7
🔢 1 : 2, 4, 8
🔢 2 : 3, 5, 9
...
```

### ❄️ Lô Gan (Numbers Not Yet Appeared)

**Purpose**: Identify lottery numbers that haven't appeared recently (also known as "cold numbers").

**Current status**: 🚧 **Beta - Using mock data**

**How it works**:
- Analyzes historical data to find numbers not appeared in N days
- Shows top 10 "coldest" numbers
- Displays how many days since last appearance

**Data source**: Mock data (will use database in future PR)

**Usage**:
1. Navigate to Statistics menu
2. Tap "❄️ Lô Gan"
3. View numbers that haven't appeared recently

**Example output**:
```
❄️ LÔ GAN (LÂU KHÔNG VỀ) - MIỀN BẮC
📊 Thống kê: 30 ngày

🔢 Các số lâu không xuất hiện:
• 00: 25 ngày
• 99: 20 ngày
• 55: 15 ngày

📝 Dữ liệu mẫu - Phiên bản beta
```

**Note**: This feature currently uses mock data. Real implementation with historical database will be available in PR #2.

## Technical Implementation

### Architecture

```
User → Telegram Bot → Handler (callbacks.py)
                         ↓
                    LotteryService (fetch results)
                         ↓
                    StatisticsService (analyze)
                         ↓
                    Formatters (display)
                         ↓
                    Telegram Message
```

### Key Components

1. **StatisticsService** (`app/services/statistics_service.py`)
   - `analyze_lo_2_so()`: Extract and analyze 2-digit numbers
   - `analyze_lo_3_so()`: Extract and analyze 3-digit numbers
   - `get_frequency_stats()`: Calculate frequency (mock for now)
   - `format_frequency_table()`: Format frequency data

2. **Formatters** (`app/ui/formatters.py`)
   - `format_lo_2_so_stats()`: Format 2-digit statistics
   - `format_lo_3_so_stats()`: Format 3-digit statistics
   - `format_lo_gan()`: Format Lô Gan data
   - `format_dau_lo()`: Format head statistics
   - `format_duoi_lo()`: Format tail statistics

3. **Mock Data** (`app/services/mock_data.py`)
   - `get_mock_lo_gan()`: Generate mock Lô Gan data

4. **Handlers** (`app/handlers/callbacks.py`)
   - Statistics callbacks for user interactions

### Data Flow

1. User taps statistics button
2. Handler receives callback
3. LotteryService fetches latest result
4. StatisticsService analyzes the data
5. Formatter creates HTML message
6. Bot sends formatted message to user

## Limitations (Current Version)

1. **Single-day analysis**: Statistics are based only on current day's results
2. **No historical trends**: Cannot show trends over multiple days
3. **Mock Lô Gan**: "Lô Gan" feature uses mock data, not real historical analysis
4. **No prediction**: Features are descriptive only, not predictive

## Future Enhancements (PR #2)

Planned features for future releases:

1. **Database Integration**
   - Store historical results (60-90 days)
   - Real Lô Gan calculation from actual history
   - True frequency analysis over time

2. **Advanced Statistics**
   - Lô Rơi (numbers that appeared yesterday but not today)
   - Bạc Nhớ (number relationships and patterns)
   - Heatmaps of number frequency
   - Trend analysis

3. **Customization**
   - Adjustable time periods (7/15/30/60 days)
   - Filter by region or province
   - Export statistics

4. **Performance**
   - Caching of statistics
   - Pre-computed analysis
   - Optimized queries

## Testing

All statistics features have comprehensive unit tests:

- `tests/test_statistics_service.py`: Service logic tests (17 tests)
- `tests/test_formatters_stats.py`: Formatter tests (21 tests)
- `tests/test_mock_data.py`: Mock data tests (includes Lô Gan tests)

**Current test coverage**: 85%+ for new code

## Usage Tips

1. **Best time to check**: After 18:30 when all results are available
2. **Frequency analysis**: Higher frequency doesn't guarantee future appearance
3. **Lô Gan**: Cold numbers may be due for appearance (gambler's fallacy warning)
4. **Multiple sources**: Cross-check with other analysis methods

## Known Issues

None at this time. All 315 tests passing.

## Support

For issues or questions about statistics features:
- Check bot /help command
- Review this documentation
- Contact: @hoangduc981998

---

**Version**: 1.0.0 (Phase 3.5)  
**Last updated**: 2025-10-15  
**Status**: ✅ Production Ready (with mock data for Lô Gan)
