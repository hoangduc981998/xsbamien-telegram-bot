"""Input sanitization utilities"""

from html import escape
import re
from typing import Optional

# Constants
MAX_MESSAGE_LENGTH = 4096  # Telegram limit
MAX_CALLBACK_DATA_LENGTH = 64  # Telegram limit
CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x1F\x7F]')  # Control characters

def sanitize_text(text: Optional[str], max_length: int = MAX_MESSAGE_LENGTH) -> str:
    """
    Sanitize user input text
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # 1. Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    # 2. Remove control characters (except newline, tab)
    text = CONTROL_CHAR_PATTERN.sub('', text)
    
    # 3. Escape HTML to prevent injection
    text = escape(text)
    
    return text.strip()

def sanitize_callback_data(data: str) -> str:
    """
    Sanitize callback data
    
    Args:
        data: Callback data string
        
    Returns:
        Sanitized callback data
    """
    if not data:
        return ""
    
    # Only allow alphanumeric, underscore, dash
    data = re.sub(r'[^a-zA-Z0-9_\-]', '', data)
    
    # Truncate
    if len(data) > MAX_CALLBACK_DATA_LENGTH:
        data = data[:MAX_CALLBACK_DATA_LENGTH]
    
    return data

def is_valid_province_code(code: str) -> bool:
    """
    Validate province code format
    
    Args:
        code: Province code
        
    Returns:
        True if valid
    """
    # Province codes: 2-6 uppercase letters
    return bool(re.match(r'^[A-Z]{2,6}$', code))
