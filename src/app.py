import sys
from PyQt5.QtWidgets import QApplication
from ui import RecorderUI
from utils import ScreenRegionSelector  # Placeholder for future region selection functionality

def main():
    """
    Entry point for the Screen Recorder application.
    
    - Initializes the QApplication.
    - Loads and displays the Recorder UI.
    - Starts the event loop.
    """
    # Initialize the Qt Application
    app = QApplication(sys.argv)

    # Create and show the main Recorder UI window
    recorder_ui = RecorderUI()
    recorder_ui.show()

    print("[INFO] Screen Recorder application started.")

    # Run the Qt event loop until the application exits
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
