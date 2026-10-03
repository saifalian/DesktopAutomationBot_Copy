from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt

class PromptDialog(QDialog):
    def __init__(self, parent=None, name="", prompt_type="system"):
        super().__init__(parent)
        self.setWindowTitle("Task Settings")
        self.setFixedSize(300, 200)
        self.init_ui(name, prompt_type)

    def init_ui(self, name, prompt_type):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Task Name:"))
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("e.g., Auto Login")
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("Prompt Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Always Follow (System)", "Initial Prompt (Start-Only)"])
        # Set current index based on type
        self.type_combo.setCurrentIndex(0 if prompt_type == "system" else 1)
        layout.addWidget(self.type_combo)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Create")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "type": "system" if self.type_combo.currentIndex() == 0 else "initial"
        }
