from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel, QComboBox, QFormLayout, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt

class BotDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Bot Setup" if data else "Create New Bot")
        self.setFixedSize(380, 320) # Made bigger for new settings
        self.init_ui(data)

    def init_ui(self, data):
        self.layout = QFormLayout(self)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., My Personal Bot")
        if data: self.name_input.setText(data.get("name", ""))
        self.layout.addRow("Bot Name:", self.name_input)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Website", "Software", "Desktop Normal"])
        if data: self.type_combo.setCurrentText(data.get("type", "Website"))
        self.type_combo.currentTextChanged.connect(self.toggle_url_field)
        self.layout.addRow("Environment:", self.type_combo)
        
        # URL (Website only)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        if data: self.url_input.setText(data.get("url", ""))
        
        # Container for URL row let's use layout logic to hide it
        self.url_label = QLabel("Website URL:")
        self.layout.addRow(self.url_label, self.url_input)
        
        self.toggle_url_field(self.type_combo.currentText())
        
        # Memory Settings
        self.use_default_memory = QCheckBox("Use Global Memory Settings")
        is_default = data.get("use_default_memory", True) if data else True
        self.use_default_memory.setChecked(is_default)
        self.use_default_memory.toggled.connect(self.toggle_memory_field)
        self.layout.addRow("Memory:", self.use_default_memory)
        
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(1, 40)
        self.memory_spin.setSuffix(" Steps")
        self.memory_spin.setValue(data.get("memory_limit", 3) if data else 3)
        self.layout.addRow("Steps to Remember:", self.memory_spin)
        
        self.toggle_memory_field(is_default)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Bot")
        self.save_btn.setStyleSheet("background-color: #2ECC71; color: white; font-weight: bold; padding: 8px;")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        self.layout.addRow(btn_layout)

    def toggle_url_field(self, text):
        visible = (text == "Website")
        self.url_input.setVisible(visible)
        self.url_label.setVisible(visible)

    def toggle_memory_field(self, is_default):
        self.memory_spin.setVisible(not is_default)
        # Find the label for memory_spin to hide/show it too
        label = self.layout.labelForField(self.memory_spin)
        if label:
            label.setVisible(not is_default)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "type": self.type_combo.currentText(),
            "url": self.url_input.text() if self.type_combo.currentText() == "Website" else "",
            "use_default_memory": self.use_default_memory.isChecked(),
            "memory_limit": self.memory_spin.value()
        }
