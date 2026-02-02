import os
import sys
from ui.app import App
from database import DatabaseManager

def enable_dpi_awareness():
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass

if __name__ == "__main__":
    enable_dpi_awareness()
    
    # Ensure DB is initialized
    db = DatabaseManager()
    
    app = App()
    app.start()
