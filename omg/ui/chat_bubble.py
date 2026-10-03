from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt

class ChatBubble(QFrame):
    def __init__(self, text, sender="user", parent=None):
        super().__init__(parent)
        self.sender = sender
        self.text = text
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Style based on sender
        if self.sender == "user":
            bg_color = "#3498DB"
            text_color = "white"
            self.setStyleSheet(f"""
                ChatBubble {{ 
                    background-color: {bg_color}; 
                    border-radius: 12px; 
                    margin-left: 40px; 
                }}
                QLabel {{ color: {text_color}; padding: 10px; font-size: 13px; }}
            """)
        else:
            bg_color = "#ECF0F1"
            text_color = "#2C3E50"
            self.setStyleSheet(f"""
                ChatBubble {{ 
                    background-color: {bg_color}; 
                    border-radius: 12px; 
                    margin-right: 40px; 
                }}
                QLabel {{ color: {text_color}; padding: 10px; font-size: 13px; }}
            """)
            
        self.label = QLabel(self.text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.label)
        
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def update_text(self, text):
        """Updates the bubble content dynamically (used for streaming)."""
        self.label.setText(text)
        self.text = text
