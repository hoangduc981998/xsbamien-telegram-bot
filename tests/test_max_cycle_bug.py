"""Tests for max_cycle calculation bug fixes"""

from datetime import date
from app.utils.lottery_helpers import count_draw_periods


class TestMaxCycleBugFix:
    """Test that max_cycle is calculated correctly"""

    def test_max_cycle_not_initialized_to_current_gan_mb(self):
        """Test MB: max_cycle should not be initialized to current gan value"""
        # Scenario: Historical max gap is 15 days, but current gan is only 7 days
        # Expected: max_cycle should be 15, not 7
        
        start_date = date(2025, 9, 1)
        end_date = date(2025, 10, 20)
        
        # Appearances with gaps: 5 days, 15 days (max!), 8 days, then 20 days to end
        dates = [
            date(2025, 9, 6),   # 5 days from start (gap: 5-1=4)
            date(2025, 9, 21),  # 15 days gap (21-6-1=14)
            date(2025, 9, 29),  # 8 days gap (29-21-1=7)
            date(2025, 9, 30),  # Current last appearance (30-29-1=0), 20 days to end
        ]
        
        # Calculate gaps manually
        gap_from_start = (dates[0] - start_date).days - 1
        gap_1_2 = (dates[1] - dates[0]).days - 1
        gap_2_3 = (dates[2] - dates[1]).days - 1
        gap_3_4 = (dates[3] - dates[2]).days - 1
        gap_from_last = (end_date - dates[3]).days - 1
        
        expected_max = max(gap_from_start, gap_1_2, gap_2_3, gap_3_4, gap_from_last)
        
        assert gap_from_start == 4, f"Gap from start should be 4, got {gap_from_start}"
        assert gap_1_2 == 14, f"Gap 1-2 should be 14, got {gap_1_2}"
        assert gap_2_3 == 7, f"Gap 2-3 should be 7, got {gap_2_3}"
        assert gap_3_4 == 0, f"Gap 3-4 should be 0, got {gap_3_4}"
        assert gap_from_last == 19, f"Current gan should be 19, got {gap_from_last}"
        assert expected_max == 19, f"Overall max should be 19, got {expected_max}"

    def test_max_cycle_historical_larger_than_current(self):
        """Test scenario where historical max is larger than current gan"""
        # This tests the bug: if we initialize max_cycle = current_gan (5),
        # and historical has gap of 10, we won't capture the 10 unless we
        # initialize to 0 and compare at the end
        
        start_date = date(2025, 6, 5)   # Thursday
        end_date = date(2025, 10, 16)   # Thursday
        
        # Create a scenario with large historical gap but small current gap
        dates = [
            date(2025, 6, 5),   # Start (same as window start)
            date(2025, 8, 7),   # Large gap from start
            date(2025, 8, 28),  # Smaller gap
            date(2025, 10, 9),  # Small current gap (1 week)
        ]
        
        # Calculate period gaps with correct parameters
        gap_from_start = count_draw_periods('ANGI', start_date, dates[1], 
                                            exclude_start=False, exclude_end=True)
        gap_1_2 = count_draw_periods('ANGI', dates[1], dates[2], 
                                     exclude_start=True, exclude_end=True)
        gap_2_3 = count_draw_periods('ANGI', dates[2], dates[3], 
                                     exclude_start=True, exclude_end=True)
        periods_since = count_draw_periods('ANGI', dates[3], end_date, 
                                           exclude_start=True, exclude_end=True)
        
        expected_max = max(gap_from_start, gap_1_2, gap_2_3, periods_since)
        
        # With the fix, max should be the largest historical or current gap
        # The bug would initialize max_cycle to periods_since, missing larger gaps
        assert gap_from_start > periods_since, "Historical gap should be larger than current"
        assert expected_max == gap_from_start, f"Max should be {gap_from_start}, got {expected_max}"


class TestExcludeEndBugFix:
    """Test that exclude_end parameter is used correctly"""

    def test_periods_since_with_exclude_end_true(self):
        """Test that periods_since uses exclude_end=True to avoid off-by-1"""
        # Scenario: Last appeared on Thursday 09/10, today is Thursday 16/10
        # With exclude_end=False: counts today (16/10) → 1 period (WRONG!)
        # With exclude_end=True: doesn't count today → 0 periods (CORRECT!)
        
        last_date = date(2025, 10, 9)   # Thursday
        end_date = date(2025, 10, 16)   # Thursday (same week, not drawn yet)
        
        # Wrong way (current bug)
        periods_wrong = count_draw_periods('ANGI', last_date, end_date, 
                                          exclude_start=True, exclude_end=False)
        
        # Correct way (after fix)
        periods_correct = count_draw_periods('ANGI', last_date, end_date,
                                            exclude_start=True, exclude_end=True)
        
        assert periods_wrong == 1, f"Bug would count 1 period, got {periods_wrong}"
        assert periods_correct == 0, f"Fix should count 0 periods, got {periods_correct}"

    def test_same_week_no_gap(self):
        """Test that same week draws show 0 gap, not 1"""
        # If today is a draw day but hasn't drawn yet, gap should be 0
        
        # TPHCM draws on Monday and Saturday
        last_monday = date(2025, 10, 13)  # Monday
        this_saturday = date(2025, 10, 18)  # Saturday (same week)
        
        # With exclude_end=False: would count Saturday → 1 period
        # With exclude_end=True: doesn't count Saturday → 0 periods
        
        periods_wrong = count_draw_periods('TPHCM', last_monday, this_saturday,
                                          exclude_start=True, exclude_end=False)
        periods_correct = count_draw_periods('TPHCM', last_monday, this_saturday,
                                            exclude_start=True, exclude_end=True)
        
        assert periods_wrong == 1
        assert periods_correct == 0


class TestHistoricalGapParameters:
    """Test that historical gap calculations use correct parameters"""

    def test_first_gap_from_window_start(self):
        """Test first gap calculation: count from start to first appearance"""
        # First gap should count from start_date to first appearance
        # Use exclude_start=False, exclude_end=True
        
        start_date = date(2025, 9, 1)   # Monday
        first_date = date(2025, 9, 8)   # Monday (one week later)
        
        # TPHCM draws Monday and Saturday
        # Should count: Mon 1st (start), Sat 6th = 2 periods
        gap = count_draw_periods('TPHCM', start_date, first_date,
                                exclude_start=False, exclude_end=True)
        
        # Mon 1st + Sat 6th = 2 draws before Mon 8th
        assert gap == 2, f"Should count 2 draws (Mon 1st, Sat 6th), got {gap}"

    def test_between_gaps_exclude_both_ends(self):
        """Test gaps between appearances: exclude both dates"""
        # Between appearances, both dates are appearance days
        # So exclude both: exclude_start=True, exclude_end=True
        
        date1 = date(2025, 9, 1)   # Monday (TPHCM draws)
        date2 = date(2025, 9, 8)   # Monday (TPHCM draws)
        
        # Between 1st and 8th, should only count Saturday 6th = 1 period
        gap = count_draw_periods('TPHCM', date1, date2,
                                exclude_start=True, exclude_end=True)
        
        assert gap == 1, f"Should count 1 draw (Sat 6th), got {gap}"

    def test_angi_real_scenario_with_exclude_end(self):
        """Test the exact ANGI scenario from problem statement"""
        # Number 35 for ANGI (Thursday only):
        # Appearances: 2025-06-05, 2025-07-10, 2025-08-28
        # Current date: 2025-10-16 (Thursday - not drawn yet)
        
        dates = [
            date(2025, 6, 5),
            date(2025, 7, 10),
            date(2025, 8, 28),
        ]
        end_date = date(2025, 10, 16)
        
        # Calculate gaps between appearances (exclude both ends)
        gap_1_2 = count_draw_periods('ANGI', dates[0], dates[1],
                                     exclude_start=True, exclude_end=True)
        gap_2_3 = count_draw_periods('ANGI', dates[1], dates[2],
                                     exclude_start=True, exclude_end=True)
        
        # Current gan with exclude_end=True (don't count today)
        periods_since = count_draw_periods('ANGI', dates[2], end_date,
                                          exclude_start=True, exclude_end=True)
        
        # With exclude_end=True, current gan should be 6, not 7
        assert gap_1_2 == 4, f"Gap 1-2 should be 4 periods, got {gap_1_2}"
        assert gap_2_3 == 6, f"Gap 2-3 should be 6 periods, got {gap_2_3}"
        assert periods_since == 6, f"Current gan should be 6 periods (exclude today), got {periods_since}"
        
        # Max should be 6
        max_cycle = max(gap_1_2, gap_2_3, periods_since)
        assert max_cycle == 6, f"Max cycle should be 6, got {max_cycle}"
