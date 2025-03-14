#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RebelDESK - A lightweight, modular IDE with AI-assisted coding capabilities.

This is the main entry point for the application. It initializes the UI and
connects it to the backend components.
"""

import sys
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rebeldesk.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add src directory to path to allow imports from other modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import QApplication
    from src.ui.main_window import MainWindow
    from src.utils.config_manager import ConfigManager
except ImportError as e:
    logger.critical(f"Failed to import required modules: {e}")
    logger.critical("Please ensure all dependencies are installed by running: pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Initialize and run the RebelDESK application."""
    try:
        logger.info("Starting RebelDESK...")
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Initialize Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName("RebelDESK")
        app.setOrganizationName("RebelDESK")
        
        # Create and show the main window
        main_window = MainWindow(config)
        main_window.show()
        
        # Start the application event loop
        logger.info("RebelDESK started successfully")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
