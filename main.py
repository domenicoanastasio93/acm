from ui.app import App
from database import DatabaseManager

if __name__ == "__main__":
    # Ensure DB is initialized
    db = DatabaseManager()
    
    app = App()
    app.start()
