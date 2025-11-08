# main.py

import sys
from PyQt6.QtWidgets import QApplication
# Import your core logger right away
from core.logger import logger

# We will define this file in the next step
from gui.main_window import TournamentApp 

def main():
    """Initializes the core modules and runs the PyQt6 application."""
    
    logger.info("Starting BracketLab Application...")

    try:
        app = QApplication(sys.argv)
        window = TournamentApp()
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Fatal unhandled exception during application run: {e}")
        # Cleanly close Loguru before exiting
        logger.complete() 
        sys.exit(1)

if __name__ == '__main__':
    main()
