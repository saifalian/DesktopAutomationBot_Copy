from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint

class OMGOverlay(QWidget):
    def __init__(self, parent_dashboard=None):
        super().__init__()
        self.dashboard = parent_dashboard
        
        # Frameless, Always on Top, Tool Window (no taskbar icon)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        self.m_drag = False
        self.m_drag_pos = QPoint()

    def init_ui(self):
        # Translucent Container
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 39, 46, 230);
                border-radius: 12px;
                border: 2px solid #3498DB;
            }
            QLabel { color: #ECF0F1; border: none; font-family: 'Segoe UI', sans-serif; }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #2980B9; }
            QPushButton#stop_btn { background-color: #E74C3C; }
            QPushButton#close_btn { 
                background-color: transparent; 
                color: #BDC3C7; 
                font-size: 14px;
            }
            QPushButton#close_btn:hover { color: #E74C3C; }
            QPushButton#play_btn[state="idle"] { background-color: #3498DB; }
            QPushButton#play_btn[state="running"] { background-color: #2ECC71; }
            QPushButton#play_btn[state="paused"] { background-color: #F39C12; }
        """)
        
        inner_layout = QVBoxLayout(self.container)
        
        # Header (Drag Handle + TOP RIGHT CLOSE)
        title_layout = QHBoxLayout()
        self.title_label = QLabel("OMG Agent")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; border: none;")
        
        self.hide_btn = QPushButton("✖")
        self.hide_btn.setObjectName("close_btn")
        self.hide_btn.setFixedSize(24, 24)
        self.hide_btn.clicked.connect(self.hide_and_sync)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.hide_btn) # Top right!
        inner_layout.addLayout(title_layout)
        
        # Status Text
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("font-size: 10px; color: #BDC3C7; padding-bottom: 5px;")
        inner_layout.addWidget(self.status_label)
        
        # Controls Row
        ctrl_layout = QHBoxLayout()
        self.play_pause_btn = QPushButton("▶") 
        self.play_pause_btn.setObjectName("play_btn")
        self.play_pause_btn.setProperty("state", "idle") # Initial Blue
        self.play_pause_btn.clicked.connect(self.toggle_local_pause)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setObjectName("stop_btn") # Red always
        self.stop_btn.clicked.connect(self.dashboard.stop_agent)
        
        ctrl_layout.addWidget(self.play_pause_btn)
        ctrl_layout.addWidget(self.stop_btn)
        inner_layout.addLayout(ctrl_layout)
        
        self.main_layout.addWidget(self.container)
        self.setFixedSize(220, 110)

    def toggle_local_pause(self):
        # Call dashboard logic
        self.dashboard.toggle_pause()
        # Update UI state
        if self.dashboard.worker and self.dashboard.worker.paused:
            self.play_pause_btn.setProperty("state", "paused")
            self.play_pause_btn.setText("▶")
        elif self.dashboard.worker:
            self.play_pause_btn.setProperty("state", "running")
            self.play_pause_btn.setText("⏸")
        else:
            self.play_pause_btn.setProperty("state", "idle")
            self.play_pause_btn.setText("▶")
        self.play_pause_btn.style().unpolish(self.play_pause_btn)
        self.play_pause_btn.style().polish(self.play_pause_btn)

    def set_running_state(self, is_running=True):
        if is_running:
            self.play_pause_btn.setProperty("state", "running")
            self.play_pause_btn.setText("⏸")
        else:
            self.play_pause_btn.setProperty("state", "idle")
            self.play_pause_btn.setText("▶")
        self.play_pause_btn.style().unpolish(self.play_pause_btn)
        self.play_pause_btn.style().polish(self.play_pause_btn)

    def update_status(self, data):
        """Called by the agent worker."""
        if isinstance(data, dict):
            thought = data.get("thought", "")
            action = data.get("action", "")
            x = data.get("x", "-")
            y = data.get("y", "-")
            text = data.get("text", "")
            
            status_text = f"🚀 {action.capitalize()}"
            if x != "-" and y != "-":
                status_text += f" at {x}%, {y}%"
            elif text:
                status_text += f": '{text}'"
                
            self.status_label.setText(status_text)
            
            # Show thought in title for transparency
            if thought:
                display_thought = thought[:45] + "..." if len(thought) > 45 else thought
                self.title_label.setText(f"🧠 {display_thought}")
        else:
            self.status_label.setText(str(data))

    def hide_and_sync(self):
        self.hide()
        # The global show_overlay_btn was removed, so we just hide the overlay.

    # --- DRAG LOGIC ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.m_drag = True
            self.m_drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.m_drag:
            self.move(event.globalPosition().toPoint() - self.m_drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_drag = False
