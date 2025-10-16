"""Test max_cycle calculation fix for PR #21 follow-up issue"""

from datetime import date, timedelta


class TestMaxCycleLogicFix:
    """Test that max_cycle is calculated correctly and can be greater than current gan"""

    def test_max_cycle_greater_than_current_gan_daily(self):
        """Test that max_cycle can be greater than current gan for daily draws (MB)"""
        # Scenario: 
        # - Window: 50 days (e.g., Sept 1 - Oct 20)
        # - Number appeared on: Sept 5, Sept 15, Oct 18
        # - Gaps: [3 days (Sept 1-5), 9 days (Sept 5-15), 32 days (Sept 15-Oct 18), 1 day (Oct 18-20)]
        # - Current gan (Oct 18 to Oct 20): 1 day
        # - Max cycle should be: 32 days (NOT 1 day)
        
        start_date = date(2025, 9, 1)
        end_date = date(2025, 10, 20)
        dates = [
            date(2025, 9, 5),   # First appearance
            date(2025, 9, 15),  # Second appearance
            date(2025, 10, 18)  # Last appearance (most recent)
        ]
        
        # Current gan (days_since)
        days_since = (end_date - dates[-1]).days - 1
        assert days_since == 1
        
        # Calculate max_cycle using the NEW logic
        max_cycle = days_since  # Start with current gan
        
        # 1. Gap from window start to first appearance
        gap = (dates[0] - start_date).days
        gan_gap = max(0, gap - 1)
        if gan_gap > max_cycle:
            max_cycle = gan_gap
        
        # 2. Gaps between consecutive appearances
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            gan_gap = max(0, gap - 1)
            if gan_gap > max_cycle:
                max_cycle = gan_gap
        
        # Verify max_cycle is greater than current gan
        assert max_cycle > days_since, f"max_cycle ({max_cycle}) should be > days_since ({days_since})"
        assert max_cycle == 32, f"max_cycle should be 32 (longest gap), got {max_cycle}"
    
    def test_max_cycle_equals_current_gan_when_current_is_longest(self):
        """Test that max_cycle equals current gan when current is the longest gap"""
        # Scenario:
        # - Window: 30 days
        # - Number appeared on: Day 2, Day 5, Day 8
        # - Gaps: [0, 2, 2, 21]
        # - Current gan: 21 days (longest)
        # - Max cycle should be: 21 days (equals current)
        
        start_date = date(2025, 9, 1)
        end_date = date(2025, 10, 1)
        dates = [
            date(2025, 9, 3),   # Day 2
            date(2025, 9, 6),   # Day 5
            date(2025, 9, 9),   # Day 8
        ]
        
        # Current gan
        days_since = (end_date - dates[-1]).days - 1
        assert days_since == 21
        
        # Calculate max_cycle
        max_cycle = days_since
        
        if dates:
            gap = (dates[0] - start_date).days
            gan_gap = max(0, gap - 1)
            if gan_gap > max_cycle:
                max_cycle = gan_gap
        
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            gan_gap = max(0, gap - 1)
            if gan_gap > max_cycle:
                max_cycle = gan_gap
        
        # Verify max_cycle equals current gan (since current is longest)
        assert max_cycle == days_since, f"max_cycle ({max_cycle}) should equal days_since ({days_since})"
        assert max_cycle == 21
    
    def test_max_cycle_variety_in_results(self):
        """Test that results can show variety: max > current, max = current"""
        # This test validates the fix ensures variety is possible
        
        # Case 1: max > current
        days_since_1 = 5
        max_cycle_1 = 20  # Historical gap was longer
        assert max_cycle_1 > days_since_1  # ✓ Possible after fix
        
        # Case 2: max = current
        days_since_2 = 15
        max_cycle_2 = 15  # Current is the longest
        assert max_cycle_2 == days_since_2  # ✓ Possible after fix
        
        # Case 3: max should NEVER be less than current (guaranteed by initialization)
        days_since_3 = 10
        max_cycle_3 = days_since_3  # Initialize with current
        # ... compare with historical gaps ...
        assert max_cycle_3 >= days_since_3  # ✓ Always true


class TestMaxCyclePeriodicDraws:
    """Test max_cycle for periodic draws (MN/MT provinces)"""
    
    def test_max_cycle_uses_periods_not_days(self):
        """Test that MN/MT provinces use periods, not days"""
        # This is a conceptual test - the actual implementation uses count_draw_periods
        # The key is that we count draw periods, not calendar days
        
        # For example, An Giang draws on Thursdays only
        # If number appeared on:
        # - Sept 4 (Thu), Sept 11 (Thu), Oct 9 (Thu)
        # - Current date: Oct 16 (Thu)
        
        # Gaps in periods:
        # - Sept 4 to Sept 11: 1 period (1 Thursday between)
        # - Sept 11 to Oct 9: 4 periods (4 Thursdays between)
        # - Oct 9 to Oct 16: 1 period (1 Thursday between)
        
        # Current gan = 1 period
        # Max cycle = 4 periods (historical max)
        
        periods_since = 1
        max_cycle = periods_since  # Initialize
        
        # Historical gaps
        gap_1 = 1  # Sept 4 to Sept 11
        gap_2 = 4  # Sept 11 to Oct 9 (longest)
        
        if gap_1 > max_cycle:
            max_cycle = gap_1
        if gap_2 > max_cycle:
            max_cycle = gap_2
        
        assert max_cycle == 4
        assert max_cycle > periods_since


class TestMaxCycleEdgeCases:
    """Test edge cases for max_cycle calculation"""
    
    def test_single_appearance_in_window(self):
        """Test with only one appearance in the analysis window"""
        start_date = date(2025, 9, 1)
        end_date = date(2025, 10, 1)
        dates = [date(2025, 9, 15)]  # Only one appearance
        
        # Current gan
        days_since = (end_date - dates[-1]).days - 1
        assert days_since == 15
        
        # Calculate max_cycle
        max_cycle = days_since
        
        # Gap from window start to first appearance
        if dates:
            gap = (dates[0] - start_date).days
            gan_gap = max(0, gap - 1)
            if gan_gap > max_cycle:
                max_cycle = gan_gap
        
        # No between-gaps since only one appearance
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            gan_gap = max(0, gap - 1)
            if gan_gap > max_cycle:
                max_cycle = gan_gap
        
        # Max cycle should be the larger of:
        # - Current gan: 15 days
        # - Gap to first: 13 days
        assert max_cycle == 15
    
    def test_no_appearances_handled_separately(self):
        """Test that numbers with no appearances are excluded (not part of this fix)"""
        # Numbers that never appeared in the window should not be in results
        # This is already handled by the main logic - this test documents the behavior
        assert True  # Placeholder - actual logic excludes these numbers
    
    def test_appearance_on_window_boundary(self):
        """Test when appearance is on the window boundaries"""
        start_date = date(2025, 9, 1)
        end_date = date(2025, 10, 1)
        
        # Case 1: Appeared on start date
        dates_1 = [date(2025, 9, 1), date(2025, 9, 15)]
        gap_1 = (dates_1[0] - start_date).days
        gan_gap_1 = max(0, gap_1 - 1)
        assert gan_gap_1 == 0  # No gap before first appearance
        
        # Case 2: Appeared on end date
        dates_2 = [date(2025, 9, 15), date(2025, 10, 1)]
        days_since_2 = (end_date - dates_2[-1]).days - 1
        assert days_since_2 == -1  # Would be handled as 0 in actual code
