import sys
import os
from PyQt6.QtWidgets import QApplication

# 1. Initialize QApplication IMMEDIATELY (prevents DPI conflicts with libraries like pyautogui)
app = QApplication(sys.argv)
app.setApplicationName("OMG")

# 2. Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 3. Now import the rest of the application
from omg.ui.dashboard import OMGDashboard
from omg.ui.overlay import OMGOverlay
from omg.utils.logger import setup_logger

def main():
    setup_logger()
    
    # Initialize Dashboard
    dashboard = OMGDashboard()
    
    # Initialize Overlay
    overlay = OMGOverlay(parent_dashboard=dashboard)
    
    # Connect UI updates between dashboard and overlay
    # Note: dashboard.show_overlay_btn handles its own toggle signal in redesign
    
    # Show main window
    dashboard.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
