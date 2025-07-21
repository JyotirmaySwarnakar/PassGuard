def copy_to_clipboard(text):
    import pyperclip
    pyperclip.copy(text)

def get_from_clipboard():
    import pyperclip
    return pyperclip.paste()