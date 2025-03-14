from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRect, QPoint, QEventLoop
import sys

class ScreenRegionSelector(QWidget):
    """
    A transparent full-screen widget for selecting a rectangular region on the screen.
    Returns the selected region as (x, y, width, height).
    """

    def __init__(self):
        super().__init__()

        # Points to track mouse press/release
        self.start_point = QPoint()
        self.end_point = QPoint()

        # The selected rectangle
        self.rect = QRect()

        # Window settings: frameless, topmost, transparent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.3)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)

        # Set geometry to full screen
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

    def mousePressEvent(self, event):
        """Capture the start point of selection."""
        self.start_point = event.pos()
        self.end_point = self.start_point
        self.update()

    def mouseMoveEvent(self, event):
        """Update the end point as the mouse moves."""
        self.end_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        """Finalize the region when the mouse is released."""
        self.end_point = event.pos()
        self.rect = QRect(self.start_point, self.end_point).normalized()
        self.close()

    def keyPressEvent(self, event):
        """Allow user to cancel selection with Escape key."""
        if event.key() == Qt.Key_Escape:
            print("[INFO] Region selection cancelled.")
            self.rect = QRect()  # No selection
            self.close()

    def paintEvent(self, event):
        """Draw the rectangle as the user selects the region."""
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 2))  # Red border
        painter.drawRect(QRect(self.start_point, self.end_point))

    @staticmethod
    def get_selected_region():
        """
        Launch the region selector widget and return the selected region.
        """
        app = QApplication.instance()
        selector = ScreenRegionSelector()

        selector.show()

        if not app:
            app = QApplication(sys.argv)
            app.exec_()  # For standalone use
        else:
            # Run a local event loop until the selector window closes
            loop = QEventLoop()
            selector.destroyed.connect(loop.quit)
            loop.exec_()

        if selector.rect.isValid():
            region = (
                selector.rect.x(),
                selector.rect.y(),
                selector.rect.width(),
                selector.rect.height()
            )
            print(f"[INFO] Region selected: {region}")
            return region
        else:
            print("[INFO] No valid region selected.")
            return None
