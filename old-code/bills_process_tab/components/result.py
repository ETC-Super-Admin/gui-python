# src/components/tabs/bills_process_tab/components/result.py
from typing import Any, Optional

class Result:
    """
    A simple result class to encapsulate operation outcomes.
    Provides a consistent way to return success/failure states with data and messages.
    """
    
    def __init__(self, success: bool, data: Any = None, message: str = "", message_type: str = "info"):
        self.success = success
        self.data = data
        self.message = message
        self.message_type = message_type  # "success", "error", "warning", "info"
    
    @classmethod
    def success(cls, data: Any = None, message: str = "") -> 'Result':
        """Create a successful result."""
        return cls(True, data, message, "success")
    
    @classmethod
    def error(cls, message: str, data: Any = None) -> 'Result':
        """Create an error result."""
        return cls(False, data, message, "error")
    
    @classmethod
    def warning(cls, message: str, data: Any = None) -> 'Result':
        """Create a warning result."""
        return cls(False, data, message, "warning")
    
    @classmethod
    def info(cls, message: str, data: Any = None) -> 'Result':
        """Create an info result."""
        return cls(True, data, message, "info")