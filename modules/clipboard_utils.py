import threading
import pyperclip

def clear_clipboard():
    pyperclip.copy('')
    print("[Clipboard] cleared.")

def copy_to_clipboard(text, clear_after=15):
    pyperclip.copy(text)
    print(f"[Clipboard] Password copied. It will be cleared in {clear_after} seconds.")
    timer = threading.Timer(clear_after, clear_clipboard)
    timer.daemon = True
    timer.start()