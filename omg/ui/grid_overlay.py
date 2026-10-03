from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class GridOverlay(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window Flags: Frameless, Always on Top, Tool window, Click-through (TransparentForInput)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.grid_enabled = False
        self.grid_opacity = 50 # 0-100
        self.grid_density = 10 # Default
        self.grid_color = QColor("#3498DB")
        
        # Set full screen (on primary monitor)
        from PyQt6.QtWidgets import QApplication
        primary_screen = QApplication.primaryScreen()
        if primary_screen:
            self.setGeometry(primary_screen.geometry())

    def update_settings(self, enabled, opacity, density, color_hex):
        self.grid_enabled = enabled
        self.grid_opacity = opacity
        self.grid_density = max(2, density) # Minimum 2x2
        self.grid_color = QColor(color_hex)
        
        if self.grid_enabled:
            self.show()
        else:
            self.hide()
        
        self.update() # Trigger repaint

    def paintEvent(self, event):
        if not self.grid_enabled:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set opacity for the painter (0-1.0)
        final_color = QColor(self.grid_color)
        final_color.setAlpha(int(2.55 * self.grid_opacity))
        
        pen = QPen(final_color, 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        
        width = self.width()
        height = self.height()
        
        # DRAW GRID based on density
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Style for Axis Labels (Red and Bold - ALWAYS PROMINENT)
        label_color = QColor("#E74C3C")
        label_color.setAlpha(255) # Always fully opaque
        label_pen = QPen(label_color, 2)
        
        # Horizontal lines
        for i in range(self.grid_density + 1):
            y = int(height * (i / self.grid_density))
            if y >= height: y = height - 1
            
            # Draw Horizontal Line (Theme Color)
            painter.setPen(pen)
            painter.drawLine(0, y, width, y)
            
            # Draw Label (Red) - Only at the start/left
            painter.setPen(label_pen)
            label = f"{int(100 * (i / self.grid_density))}"
            painter.drawText(5, y - 2, label)
            
        # Vertical lines
        for i in range(self.grid_density + 1):
            x = int(width * (i / self.grid_density))
            if x >= width: x = width - 1
            
            # Draw Vertical Line (Theme Color)
            painter.setPen(pen)
            painter.drawLine(x, 0, x, height)
            
            # Draw Label (Red) - Only at the top
            painter.setPen(label_pen)
            label = f"{int(100 * (i / self.grid_density))}"
            painter.drawText(x + 2, 15, label)

        # Intersection crosses (Theme Color)
        painter.setPen(pen) # SWITCH BACK TO GRID PEN
        cross_size = 3
        for row in range(1, self.grid_density):
            for col in range(1, self.grid_density):
                px = int(width * (col / self.grid_density))
                py = int(height * (row / self.grid_density))
                painter.drawLine(px - cross_size, py, px + cross_size, py)
                painter.drawLine(px, py - cross_size, px, py + cross_size)

