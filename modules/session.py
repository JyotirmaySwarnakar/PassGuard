import time
import threading

class SessionManager:
    def __init__(self, timeout_seconds=20):
        self.timeout = timeout_seconds
        self.locked = False
        self._timer = None
        self.refresh()  # Start the timer

    def _start_timer(self):
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.timeout, self.lock)
        self._timer.daemon = True
        self._timer.start()

    def refresh(self):
        """Call this after every user action to reset the timer."""
        self.locked = False
        self._start_timer()

    def lock(self):
        self.locked = True
        # Do not print here; let main handle the message

    def is_locked(self):
        return self.locked

    def stop(self):
        if self._timer:
            self._timer.cancel()

def create_session(user_id):
    # Logic to create a new user session
    pass

def validate_session(session_id):
    # Logic to validate an existing session
    pass

def terminate_session(session_id):
    # Logic to terminate a user session
    pass

def get_current_user(session_id):
    # Logic to retrieve the current user based on the session ID
    pass

# This file is intentionally left blank.