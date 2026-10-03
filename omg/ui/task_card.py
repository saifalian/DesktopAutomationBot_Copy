from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

class TaskCard(QFrame):
    start_clicked = pyqtSignal(dict) # Emits task data
    stop_clicked = pyqtSignal()
    delete_clicked = pyqtSignal(object) # Emits self for deletion
    edit_clicked = pyqtSignal(object)   # Emits self for editing

    def __init__(self, name, prompt_type, parent=None):
        super().__init__(parent)
        self.name = name
        self.prompt_type = prompt_type
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            TaskCard { 
                background-color: #f9f9f9; 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 10px;
                margin-bottom: 2px;
            }
            QLabel#task_name { font-weight: bold; color: #2C3E50; font-size: 14px; }
            QLabel#task_type { color: #7F8C8D; font-style: italic; }
            QPushButton#start_btn { background-color: #2ECC71; color: white; border-radius: 4px; padding: 5px; }
            QPushButton#stop_btn { background-color: #E74C3C; color: white; border-radius: 4px; padding: 5px; }
            QPushButton.icon_btn { background-color: transparent; border: none; font-size: 14px; color: #7F8C8D; }
            QPushButton.icon_btn:hover { color: #E74C3C; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header (Name, Type, and Actions)
        header = QHBoxLayout()
        
        self.name_label = QLabel(self.name)
        self.name_label.setObjectName("task_name")
        self.type_label = QLabel(f"({self.prompt_type.capitalize()})")
        self.type_label.setObjectName("task_type")
        
        header.addWidget(self.name_label)
        header.addWidget(self.type_label)
        header.addStretch()
        
        # Edit & Delete Buttons
        self.edit_btn = QPushButton("✏️")
        self.edit_btn.setToolTip("Rename / Change Type")
        self.edit_btn.setFixedSize(24, 24)
        self.edit_btn.setProperty("class", "icon_btn") # CSS selector
        self.edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self))
        
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setToolTip("Delete Task")
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setProperty("class", "icon_btn")
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self))
        
        header.addWidget(self.edit_btn)
        header.addWidget(self.delete_btn)
        
        layout.addLayout(header)
        
        # Prompt Editor
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText(f"Enter {self.prompt_type} prompt here...")
        self.prompt_edit.setFixedHeight(100)
        layout.addWidget(self.prompt_edit)

    def reset_controls(self):
        pass
