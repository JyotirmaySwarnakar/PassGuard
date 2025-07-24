#!/usr/bin/env python3
"""
Session Management Module
Handles user session timeouts and auto-lock functionality.
"""

import time
import threading

class SessionManager:
    """
    Manages user sessions with automatic timeout and lock functionality.
    
    Features:
    - Configurable timeout period
    - Automatic session locking on inactivity
    - Thread-safe timer management
    - Session refresh capability
    """
    
    def __init__(self, timeout_seconds=180):
        """
        Initialize session manager.
        
        Args:
            timeout_seconds (int): Session timeout in seconds (default: 180)
        """
        self.timeout = timeout_seconds
        self.locked = False
        self._timer = None
        self._lock = threading.Lock()
        
    def _start_timer(self):
        """Start or restart the session timeout timer."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.timeout, self._auto_lock)
            self._timer.daemon = True
            self._timer.start()
    
    def _auto_lock(self):
        """Automatically lock the session (called by timer)."""
        with self._lock:
            self.locked = True
    
    def refresh(self):
        """
        Refresh the session, resetting the timeout timer.
        Call this method after every user interaction.
        """
        with self._lock:
            self.locked = False
        self._start_timer()
    
    def lock(self):
        """Manually lock the session."""
        with self._lock:
            self.locked = True
            if self._timer:
                self._timer.cancel()
    
    def is_locked(self):
        """
        Check if the session is currently locked.
        
        Returns:
            bool: True if session is locked, False otherwise
        """
        with self._lock:
            return self.locked
    
    def stop(self):
        """Stop the session manager and cancel any active timers."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None
    
    def get_remaining_time(self):
        """
        Get remaining time before session locks.
        
        Returns:
            int: Remaining seconds (approximation)
        """
        # Note: This is an approximation since we don't track exact start time
        return self.timeout if not self.is_locked() else 0