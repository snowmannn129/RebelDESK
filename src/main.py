#!/usr/bin/env python3
"""
RebelDESK - Main entry point for the application.
"""

import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path.home() / "rebeldesk.log"),
    ],
)
logger = logging.getLogger("RebelDESK")

def main():
    """
    Main entry point for the RebelDESK application.
    """
    try:
        # Import PyQt here to avoid importing it when the module is imported
        from PyQt5.QtWidgets import QApplication
        
        # Import the main window
        from rebeldesk.ui.main_window import MainWindow
        
        # Create the application
        app = QApplication(sys.argv)
        app.setApplicationName("RebelDESK")
        app.setOrganizationName("RebelSUITE")
        app.setOrganizationDomain("rebelsuite.com")
        
        # Create and show the main window
        main_window = MainWindow()
        main_window.show()
        
        # Start the application event loop
        sys.exit(app.exec_())
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        print(f"Error: Failed to import required modules: {e}")
        print("Please make sure all dependencies are installed by running:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        print(f"Error: An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
