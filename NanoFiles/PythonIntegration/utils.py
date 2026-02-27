import sys
import os

def resource_path(relative_path):
    """Read-only path — bundled assets (STL, default JSON)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def writable_path(relative_path):
    """
    Writable path for user data (baseline JSON).
    Saves next to the .exe on Windows/Mac so it persists between runs.
    """
    if hasattr(sys, '_MEIPASS'):
        # Save alongside the .exe in dist/
        exe_dir = os.path.dirname(sys.executable)
    else:
        # Dev mode — save in current working directory
        exe_dir = os.path.abspath(".")
    return os.path.join(exe_dir, relative_path)
