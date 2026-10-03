from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

class BotCard(QFrame):
    edit_clicked = pyqtSignal(object)
    delete_clicked = pyqtSignal(object)
    open_clicked = pyqtSignal(object)
    open_overlay_clicked = pyqtSignal(object)

    def __init__(self, bot_data):
        super().__init__()
        self.bot_data = bot_data
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("bot_card")
        self.setFixedWidth(300)
        self.setFixedHeight(180)
        self.setStyleSheet("""
            QFrame#bot_card {
                background-color: #F7F9F9;
                border: 2px solid #D5DBDB;
                border-radius: 15px;
            }
            QLabel#bot_name { font-weight: bold; font-size: 18px; color: #2C3E50; }
            QLabel#bot_type { font-size: 13px; color: #7F8C8D; }
            QPushButton { border: none; padding: 10px; border-radius: 8px; font-size: 14px; }
            QPushButton:hover { background-color: #EAECEE; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header (Name + Edit/Delete)
        header = QHBoxLayout()
        self.name_label = QLabel(self.bot_data.get("name", "Unnamed Bot"))
        self.name_label.setObjectName("bot_name")
        self.name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.name_label.mousePressEvent = lambda e: self.open_clicked.emit(self)
        header.addWidget(self.name_label)
        header.addStretch()
        
        self.edit_btn = QPushButton("✏️")
        self.edit_btn.setToolTip("Edit Bot")
        self.edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self))
        header.addWidget(self.edit_btn)
        
        self.del_btn = QPushButton("🗑️")
        self.del_btn.setToolTip("Delete Bot")
        self.del_btn.clicked.connect(lambda: self.delete_clicked.emit(self))
        header.addWidget(self.del_btn)
        layout.addLayout(header)
        
        # Info
        type_text = self.bot_data.get("type", "Desktop")
        if self.bot_data.get("url"):
            type_text += f"\n({self.bot_data['url']})"
        self.type_label = QLabel(type_text)
        self.type_label.setObjectName("bot_type")
        self.type_label.setWordWrap(True)
        layout.addWidget(self.type_label)
        
        layout.addStretch()
        
        # Actions Row
        actions = QHBoxLayout()
        self.open_btn = QPushButton("⚙️ Setup Bot")
        self.open_btn.setStyleSheet("""
            background-color: #BDC3C7; color: #2C3E50; font-weight: bold; padding: 6px;
        """)
        self.open_btn.clicked.connect(lambda: self.open_clicked.emit(self))
        
        self.run_btn = QPushButton("▶ Run Bot")
        self.run_btn.setStyleSheet("""
            background-color: #2ECC71; color: white; font-weight: bold; padding: 6px;
        """)
        self.run_btn.clicked.connect(lambda: self.open_overlay_clicked.emit(self))
        
        actions.addWidget(self.open_btn)
        actions.addWidget(self.run_btn)
        layout.addLayout(actions)
