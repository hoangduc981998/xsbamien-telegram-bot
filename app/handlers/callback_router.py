"""Callback Router - Clean callback handling with router pattern"""

import logging
from typing import Callable, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class CallbackRouter:
    """Router for handling callback queries"""
    
    def __init__(self):
        self.routes: Dict[str, Callable] = {}
    
    def register(self, prefix: str, handler: Callable):
        """
        Register a callback handler
        
        Args:
            prefix: Callback prefix (e.g., 'result', 'stats')
            handler: Async handler function
        """
        self.routes[prefix] = handler
        logger.debug(f"Registered route: {prefix}")
    
    async def route(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        callback_data: str
    ) -> bool:
        """
        Route callback to appropriate handler
        
        Args:
            update: Telegram update
            context: Bot context
            callback_data: Full callback data string
            
        Returns:
            True if routed successfully, False otherwise
        """
        # Parse callback data
        parts = callback_data.split("_", 1)
        prefix = parts[0]
        argument = parts[1] if len(parts) > 1 else None
        
        # Find handler
        handler = self.routes.get(prefix)
        
        if handler:
            try:
                await handler(update, context, argument)
                return True
            except Exception as e:
                logger.exception(f"Error in callback handler '{prefix}': {e}")
                # Send error message to user
                query = update.callback_query
                try:
                    await query.edit_message_text(
                        "❌ Có lỗi xảy ra. Vui lòng thử lại.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🏠 Trang chủ", callback_data="main_menu")
                        ]])
                    )
                except Exception:
                    pass
                return False
        
        logger.warning(f"No handler found for callback prefix: {prefix}")
        return False


# Global router instance
router = CallbackRouter()
