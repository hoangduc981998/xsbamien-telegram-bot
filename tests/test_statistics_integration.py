"""Integration tests for statistics callbacks"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.handlers.callbacks import button_callback


class TestStatisticsCallbacks:
    """Test new statistics callback handlers"""

    @pytest.mark.asyncio
    async def test_stats_lo2_callback_with_data(self):
        """Test Lô 2 số callback handler with mock data"""
        # Mock update and context
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_lo2_MB"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        # Mock services
        with patch('app.handlers.callbacks.statistics_service') as mock_stats:
            mock_stats.get_frequency_stats = AsyncMock(return_value={
                '00': 5, '01': 3, '02': 7, '03': 2
            })
            
            # Call handler
            await button_callback(update, context)
            
            # Verify answer was called
            query.answer.assert_called_once()
            
            # Verify edit_message_text was called
            query.edit_message_text.assert_called_once()
            
            # Check message content
            call_args = query.edit_message_text.call_args
            message = call_args[0][0] if call_args[0] else call_args[1]['text']
            
            assert "THỐNG KÊ LÔ 2 SỐ" in message
            assert "MIỀN BẮC" in message or "MB" in message

    @pytest.mark.asyncio
    async def test_stats_lo2_callback_no_data(self):
        """Test Lô 2 số callback handler with no data"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_lo2_TPHCM"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.statistics_service') as mock_stats:
            mock_stats.get_frequency_stats = AsyncMock(return_value={})
            
            await button_callback(update, context)
            
            query.answer.assert_called_once()
            query.edit_message_text.assert_called_once()
            
            # Check message shows no data warning
            call_args = query.edit_message_text.call_args
            message = call_args[0][0] if call_args[0] else call_args[1]['text']
            assert "Chưa có dữ liệu" in message

    @pytest.mark.asyncio
    async def test_stats_lo3_callback_with_data(self):
        """Test Lô 3 số callback handler"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_lo3_MB"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.statistics_service') as mock_stats:
            mock_stats.get_lo3so_frequency_stats = AsyncMock(return_value={
                '000': 2, '123': 5, '456': 3
            })
            
            await button_callback(update, context)
            
            query.answer.assert_called_once()
            query.edit_message_text.assert_called_once()
            
            call_args = query.edit_message_text.call_args
            message = call_args[0][0] if call_args[0] else call_args[1]['text']
            assert "THỐNG KÊ LÔ 3 SỐ" in message

    @pytest.mark.asyncio
    async def test_stats_dau_callback(self):
        """Test Đầu Lô callback handler"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_dau_MB"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        # Mock lottery service
        with patch('app.handlers.callbacks.lottery_service') as mock_lottery:
            mock_lottery.get_latest_result = AsyncMock(return_value={
                'date': '2025-10-16',
                'prizes': {
                    'DB': ['12345'],
                    'G1': ['67890'],
                    'G7': ['01', '23', '45', '67']
                }
            })
            
            await button_callback(update, context)
            
            query.answer.assert_called_once()
            query.edit_message_text.assert_called_once()
            
            call_args = query.edit_message_text.call_args
            message = call_args[0][0] if call_args[0] else call_args[1]['text']
            assert "THỐNG KÊ ĐẦU LÔ" in message

    @pytest.mark.asyncio
    async def test_stats_duoi_callback(self):
        """Test Đuôi Lô callback handler"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_duoi_TPHCM"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.lottery_service') as mock_lottery:
            mock_lottery.get_latest_result = AsyncMock(return_value={
                'date': '2025-10-16',
                'prizes': {
                    'DB': ['123456'],
                    'G1': ['78901'],
                    'G8': ['23']
                }
            })
            
            await button_callback(update, context)
            
            query.answer.assert_called_once()
            query.edit_message_text.assert_called_once()
            
            call_args = query.edit_message_text.call_args
            message = call_args[0][0] if call_args[0] else call_args[1]['text']
            assert "THỐNG KÊ ĐUÔI LÔ" in message

    @pytest.mark.asyncio
    async def test_callback_back_button_present(self):
        """Test that back button is present in statistics views"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_lo2_MB"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.statistics_service') as mock_stats:
            mock_stats.get_frequency_stats = AsyncMock(return_value={'00': 1})
            
            await button_callback(update, context)
            
            # Check that keyboard has back button
            call_args = query.edit_message_text.call_args
            keyboard = call_args[1]['reply_markup']
            
            # Find back button
            has_back = False
            for row in keyboard.inline_keyboard:
                for button in row:
                    if "Quay lại" in button.text:
                        has_back = True
                        # Verify it goes back to result
                        assert button.callback_data.startswith("result_")
                        break
            
            assert has_back, "Back button not found in keyboard"

    @pytest.mark.asyncio
    async def test_error_handling_stats_lo2(self):
        """Test error handling in stats_lo2 callback"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_lo2_MB"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.statistics_service') as mock_stats:
            # Simulate error
            mock_stats.get_frequency_stats = AsyncMock(side_effect=Exception("Test error"))
            
            await button_callback(update, context)
            
            query.answer.assert_called_once()
            query.edit_message_text.assert_called_once()
            
            # Check error message
            call_args = query.edit_message_text.call_args
            message = call_args[0][0] if call_args[0] else call_args[1]['text']
            assert "Lỗi" in message or "lỗi" in message

    @pytest.mark.asyncio
    async def test_error_handling_stats_dau(self):
        """Test error handling in stats_dau callback"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_dau_DANA"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.lottery_service') as mock_lottery:
            mock_lottery.get_latest_result = AsyncMock(side_effect=Exception("API error"))
            
            await button_callback(update, context)
            
            query.answer.assert_called_once()
            query.edit_message_text.assert_called_once()
            
            call_args = query.edit_message_text.call_args
            message = call_args[0][0] if call_args[0] else call_args[1]['text']
            assert "Lỗi" in message or "lỗi" in message


class TestResultDisplayIntegration:
    """Test result display with new statistics buttons"""

    @pytest.mark.asyncio
    async def test_result_callback_uses_new_keyboard(self):
        """Test that result callback uses new combined keyboard"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "result_MB"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.lottery_service') as mock_lottery:
            mock_lottery.get_latest_result = AsyncMock(return_value={
                'date': '2025-10-16',
                'prizes': {
                    'DB': ['12345'],
                    'G1': ['67890']
                }
            })
            
            await button_callback(update, context)
            
            # Check keyboard has new buttons
            call_args = query.edit_message_text.call_args
            keyboard = call_args[1]['reply_markup']
            
            # Get all button texts
            button_texts = []
            for row in keyboard.inline_keyboard:
                for button in row:
                    button_texts.append(button.text)
            
            # Verify new buttons are present
            assert "📊 Lô 2 số" in button_texts
            assert "🎰 Lô 3 số" in button_texts
            assert "🔢 Đầu Lô" in button_texts
            assert "🔢 Đuôi Lô" in button_texts

    @pytest.mark.asyncio
    async def test_province_code_preserved_across_navigation(self):
        """Test province code is preserved in navigation"""
        province_code = "TPHCM"
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = f"result_{province_code}"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.lottery_service') as mock_lottery:
            mock_lottery.get_latest_result = AsyncMock(return_value={
                'date': '2025-10-16',
                'province': 'TP.HCM',
                'prizes': {'DB': ['123456']}
            })
            
            await button_callback(update, context)
            
            # Check all stats buttons have correct province code
            call_args = query.edit_message_text.call_args
            keyboard = call_args[1]['reply_markup']
            
            for row in keyboard.inline_keyboard:
                for button in row:
                    if button.callback_data.startswith("stats_"):
                        assert button.callback_data.endswith(province_code), \
                            f"Button {button.text} doesn't preserve province code"


class TestBackNavigation:
    """Test back navigation from statistics views"""

    @pytest.mark.asyncio
    async def test_back_from_lo2_to_result(self):
        """Test back button from Lô 2 số returns to result"""
        # First, view stats
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_lo2_MB"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.statistics_service') as mock_stats:
            mock_stats.get_frequency_stats = AsyncMock(return_value={'00': 1})
            
            await button_callback(update, context)
            
            # Get back button callback
            call_args = query.edit_message_text.call_args
            keyboard = call_args[1]['reply_markup']
            
            back_callback = None
            for row in keyboard.inline_keyboard:
                for button in row:
                    if "Quay lại kết quả" in button.text:
                        back_callback = button.callback_data
                        break
            
            assert back_callback == "result_MB"

    @pytest.mark.asyncio
    async def test_back_from_dau_preserves_province(self):
        """Test back button preserves province context"""
        update = MagicMock()
        context = MagicMock()
        query = update.callback_query
        query.data = "stats_dau_ANGI"
        query.answer = AsyncMock()
        query.edit_message_text = AsyncMock()
        
        with patch('app.handlers.callbacks.lottery_service') as mock_lottery:
            mock_lottery.get_latest_result = AsyncMock(return_value={
                'date': '2025-10-16',
                'prizes': {'DB': ['12345']}
            })
            
            await button_callback(update, context)
            
            call_args = query.edit_message_text.call_args
            keyboard = call_args[1]['reply_markup']
            
            # Find back button
            back_callback = None
            for row in keyboard.inline_keyboard:
                for button in row:
                    if "Quay lại" in button.text and button.callback_data.startswith("result_"):
                        back_callback = button.callback_data
            
            assert back_callback == "result_ANGI"
