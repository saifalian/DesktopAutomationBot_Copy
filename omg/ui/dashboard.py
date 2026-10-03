import os
import json
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QLabel, QLineEdit, QPushButton, QGroupBox, QScrollArea,
    QFormLayout, QSpinBox, QDoubleSpinBox, QFrame, QCheckBox, 
    QApplication, QTextEdit, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from omg.ui.worker import AgentWorker
from omg.ui.prompt_dialog import PromptDialog
from omg.ui.task_card import TaskCard
from omg.ui.overlay import OMGOverlay
from omg.ui.bot_dialog import BotDialog
from omg.ui.bot_card import BotCard
from omg.ui.bot_interface_dialog import BotInterfaceDialog
from omg.ui.grid_overlay import GridOverlay # New Import

class OMGDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OMG: Autonomous Visual AI Agent")
        self.resize(1000, 800)
        
        # Paths
        self.config_dir = os.path.join(os.path.expanduser("~"), ".omg")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.config_file = os.path.join(self.config_dir, "tasks.json")
        self.session_file = os.path.join(self.config_dir, "sessions.json")
        self.bots_file = os.path.join(self.config_dir, "bots.json")
        self.bots_ocr_file = os.path.join(self.config_dir, "bots_ocr.json")
        
        # State
        from omg.agent.memory_sessions import SessionManager
        self.session_manager = SessionManager()
        self.load_sessions()
        self.config = {
            "base_url": "http://localhost:1234/v1",
            "model_id": "qwen2-vl-7b-instruct",
            "temperature": 0.2,
            "max_history": 3,
            "action_delay": 1.5,
            "permissions_granted": True,
            "grid_enabled": False,
            "grid_opacity": 50,
            "grid_density": 10,
            "system_prompt": "",
            "chat_system_prompt": "You are OMG, a helpful and knowledgeable AI assistant. Answer the user's questions clearly, concisely, and helpfully."
        }
        self.worker = None
        self.grid_overlay = GridOverlay() # Initialize New Overlay
        self.task_cards = []
        self.bot_cards = []
        self.ocr_bot_cards = []
        self.current_bot_data = None # Active bot context for overlay
        self.current_bot_type = "bot" # "bot" or "ocr"
        self.overlay = OMGOverlay(parent_dashboard=self)
        self.pending_image_path = None # For manual attachments
        
        self.init_ui()
        self.load_tasks()
        self.load_bots()
        self.load_ocr_bots()
        self.update_session_list()
        self.on_session_clicked(self.session_list.item(0))

        # Chat Memory
        from omg.agent.memory import ShortMemory
        from omg.llm.client import LLMClient
        from omg.vision.screenshot import ScreenShotter
        from omg.vision.preprocess import ImagePreprocessor
        
        self.chat_memory = ShortMemory(max_steps=10)
        self.chat_client = LLMClient(base_url=self.config["base_url"])
        self.chat_screenshotter = ScreenShotter()
        self.chat_preprocessor = ImagePreprocessor()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        self.header = QLabel("OMG - Autonomous AI Agent")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498DB;")
        header_layout.addWidget(self.header)
        header_layout.addStretch()
        
        self.layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.create_chat_tab()
        self.create_bot_tab()
        self.create_ocr_tab()
        self.create_prompts_tab()
        self.create_settings_tab()
        self.tabs.setCurrentIndex(0)

    def create_prompts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create Task Button
        create_btn_layout = QHBoxLayout()
        self.create_task_btn = QPushButton("➕ Create New Task Section")
        self.create_task_btn.setStyleSheet("""
            background-color: #3498DB; color: white; padding: 15px; 
            font-weight: bold; border-radius: 8px; font-size: 14px;
        """)
        self.create_task_btn.clicked.connect(self.show_prompt_dialog)
        create_btn_layout.addWidget(self.create_task_btn)
        layout.addLayout(create_btn_layout)
        
        # Scroll Area for Dynamic Task Sections
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_content = QWidget()
        self.tasks_layout = QVBoxLayout(self.scroll_content)
        self.tasks_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        
        self.tabs.addTab(tab, "📝 Prompts")

    def create_bot_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header with Create Bot button
        top_bar = QHBoxLayout()
        title = QLabel("🤖 My AI Bots")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar.addWidget(title)
        top_bar.addStretch()
        
        self.create_bot_btn = QPushButton("➕ Create a Bot")
        self.create_bot_btn.setStyleSheet("""
            background-color: #2ECC71; color: white; padding: 10px 20px; 
            font-weight: bold; border-radius: 5px;
        """)
        self.create_bot_btn.clicked.connect(self.show_bot_dialog)
        top_bar.addWidget(self.create_bot_btn)
        layout.addLayout(top_bar)
        
        # Bot Horizontal Scroll/Flow Area
        self.bot_scroll = QScrollArea()
        self.bot_scroll.setWidgetResizable(True)
        self.bot_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.bot_container = QWidget()
        self.bot_layout = QHBoxLayout(self.bot_container)
        self.bot_layout.addStretch()
        self.bot_scroll.setWidget(self.bot_container)
        layout.addWidget(self.bot_scroll)
        
        layout.addStretch() # Take up remaining space
        
        self.tabs.addTab(tab, "🤖 Bot")

    def create_ocr_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header with Create OCR Bot button
        top_bar = QHBoxLayout()
        title = QLabel("👁️ OCR AI Bots")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar.addWidget(title)
        top_bar.addStretch()
        
        self.create_ocr_bot_btn = QPushButton("👁️ Create OCR Bot")
        self.create_ocr_bot_btn.setStyleSheet("""
            background-color: #9B59B6; color: white; padding: 10px 20px; 
            font-weight: bold; border-radius: 5px;
        """)
        self.create_ocr_bot_btn.clicked.connect(self.show_ocr_bot_dialog)
        top_bar.addWidget(self.create_ocr_bot_btn)
        layout.addLayout(top_bar)
        
        # OCR Bot Horizontal Scroll Area
        self.ocr_bot_scroll = QScrollArea()
        self.ocr_bot_scroll.setWidgetResizable(True)
        self.ocr_bot_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.ocr_bot_container = QWidget()
        self.ocr_bot_layout = QHBoxLayout(self.ocr_bot_container)
        self.ocr_bot_layout.addStretch()
        self.ocr_bot_scroll.setWidget(self.ocr_bot_container)
        layout.addWidget(self.ocr_bot_scroll)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "👁️ OCR AI")

    def create_chat_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Sidebar (Left)
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("background-color: #202123; border-right: 1px solid #4D4D4F;")
        sb_layout = QVBoxLayout(sidebar)
        
        self.new_chat_btn = QPushButton("➕ New Chat")
        self.new_chat_btn.setStyleSheet("""
            background-color: transparent; color: white; border: 1px solid #4D4D4F; 
            padding: 10px; border-radius: 5px; text-align: left;
        """)
        self.new_chat_btn.clicked.connect(self.start_new_chat)
        sb_layout.addWidget(self.new_chat_btn)
        
        from PyQt6.QtWidgets import QListWidget
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("background-color: transparent; color: #ECECF1; border: none;")
        self.session_list.itemClicked.connect(self.on_session_clicked)
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self.show_chat_context_menu)
        sb_layout.addWidget(self.session_list)
        layout.addWidget(sidebar)
        
        # 2. Main Chat Area
        main_area = QWidget()
        main_layout = QVBoxLayout(main_area)
        
        # Model Indicator (Top)
        model_panel = QHBoxLayout()
        self.model_label = QLabel(f"🤖 Model: {self.config['model_id']}")
        self.model_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        model_panel.addWidget(self.model_label)
        model_panel.addStretch()
        main_layout.addLayout(model_panel)
        
        # Scrollable History
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_viewport = QWidget()
        self.chat_v_layout = QVBoxLayout(self.chat_viewport)
        self.chat_v_layout.addStretch()
        self.chat_scroll.setWidget(self.chat_viewport)
        main_layout.addWidget(self.chat_scroll)
        
        # Bottom Input Area
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: #F7F7F8; 
                border-top: 1px solid #D5DBDB; 
                border-radius: 15px;
            }
        """)
        bottom_layout = QHBoxLayout(input_container)
        
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setFixedSize(40, 40)
        self.attach_btn.setStyleSheet("border: none; font-size: 18px; color: #7F8C8D;")
        self.attach_btn.setToolTip("Attach Image from System")
        self.attach_btn.clicked.connect(self.on_attach_clicked)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Message OMG...")
        self.chat_input.setStyleSheet("""
            border: none; 
            padding: 10px; 
            font-size: 14px; 
            background: transparent;
            color: #202123;  /* Ensure visibility */
        """)
        self.chat_input.returnPressed.connect(self.send_chat_message)
        
        self.send_chat_btn = QPushButton("⬆")
        self.send_chat_btn.setFixedSize(32, 32)
        self.send_chat_btn.setStyleSheet("""
            QPushButton { 
                background-color: #202123; color: white; border-radius: 5px; font-weight: bold; font-size: 16px;
            }
            QPushButton:disabled { background-color: #D5DBDB; color: #7F8C8D; }
            QPushButton:hover { background-color: #3498DB; }
        """)
        self.send_chat_btn.clicked.connect(self.send_chat_message)
        
        bottom_layout.addWidget(self.attach_btn)
        bottom_layout.addWidget(self.chat_input)
        bottom_layout.addWidget(self.send_chat_btn)
        main_layout.addWidget(input_container)
        
        # Loading Indicator (Hidden)
        self.chat_loading_label = QLabel(" 🤖 OMG is thinking...")
        self.chat_loading_label.setStyleSheet("color: #7F8C8D; font-style: italic; font-size: 11px;")
        self.chat_loading_label.hide()
        main_layout.addWidget(self.chat_loading_label)
        
        layout.addWidget(main_area)
        self.tabs.addTab(tab, "💬 Chat")

    def create_settings_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        self.url_input = QLineEdit(self.config["base_url"])
        layout.addRow("LM Studio Server:", self.url_input)
        self.model_input = QLineEdit(self.config["model_id"])
        
        # Model Row with Sync Button
        model_layout = QHBoxLayout()
        model_layout.addWidget(self.model_input)
        self.sync_model_btn = QPushButton("🔄 Sync from LM Studio")
        self.sync_model_btn.setStyleSheet("""
            QPushButton { background-color: #7F8C8D; color: white; padding: 4px 8px; font-size: 11px; }
            QPushButton:hover { background-color: #95A5A6; }
        """)
        self.sync_model_btn.clicked.connect(self.auto_sync_model)
        model_layout.addWidget(self.sync_model_btn)
        
        layout.addRow("Model ID:", model_layout)
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0, 1.0)
        self.temp_spin.setValue(self.config["temperature"])
        layout.addRow("Temperature:", self.temp_spin)
        self.history_spin = QSpinBox()
        self.history_spin.setRange(1, 10)
        self.history_spin.setValue(self.config["max_history"])
        layout.addRow("Memory Context Steps:", self.history_spin)
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setValue(self.config["action_delay"])
        layout.addRow("Action Delay (sec):", self.delay_spin)
        
        self.perm_check = QCheckBox("Grant System Permissions (Screen Recording & Input Control)")
        self.perm_check.setChecked(self.config.get("permissions_granted", False))
        layout.addRow("Security:", self.perm_check)
        
        # Grid Section - Added as requested "after the setting section"
        self.create_grid_settings(layout)
        
        # Chat Settings Section
        self.create_chat_settings(layout)
        
        # Add Logs Section in Settings
        self.create_logs_section(layout)
        
        self.tabs.addTab(tab, "Settings")

    def create_chat_settings(self, parent_layout):
        chat_group = QGroupBox("💬 Chat Interaction")
        chat_layout = QVBoxLayout(chat_group)
        
        chat_layout.addWidget(QLabel("Chat System Prompt (Instructions for the AI in Chat tab):"))
        self.chat_system_prompt_edit = QTextEdit()
        
        current_chat_sys = self.config.get("chat_system_prompt", "YOU ARE 'OMG', A POWERFUL VISUAL AI. You help the user understand their screen or images.").strip()
        self.chat_system_prompt_edit.setPlainText(current_chat_sys)
        self.chat_system_prompt_edit.setPlaceholderText("Enter instructions for how the AI should behave in Chat...")
        self.chat_system_prompt_edit.setFixedHeight(120) 
        chat_layout.addWidget(self.chat_system_prompt_edit)
        
        parent_layout.addRow(chat_group)

    def create_grid_settings(self, parent_layout):
        grid_group = QGroupBox("🌐 Grid Layer")
        grid_layout = QVBoxLayout(grid_group)
        
        # Toggles and controls
        h_ctrl = QHBoxLayout()
        self.grid_check = QCheckBox("Enable Visual Grid Overlay (10x10 Coordinate Guide)")
        self.grid_check.setChecked(self.config.get("grid_enabled", False))
        self.grid_check.toggled.connect(self.sync_grid_from_ui)
        
        h_ctrl.addWidget(self.grid_check)
        h_ctrl.addStretch()
        
        self.grid_to_ai_check = QCheckBox("Burn Grid into AI Screenshot (Helps AI precision)")
        self.grid_to_ai_check.setChecked(self.config.get("grid_to_ai", False))
        h_ctrl.addWidget(self.grid_to_ai_check)
        
        grid_layout.addLayout(h_ctrl)
        
        # Opacity Slider
        from PyQt6.QtWidgets import QSlider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Grid Opacity:"))
        self.grid_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.grid_opacity_slider.setRange(5, 100)
        self.grid_opacity_slider.setValue(self.config.get("grid_opacity", 50))
        self.grid_opacity_slider.valueChanged.connect(self.sync_grid_from_ui)
        opacity_layout.addWidget(self.grid_opacity_slider)
        
        grid_layout.addLayout(opacity_layout)

        # Density Control
        density_layout = QHBoxLayout()
        density_layout.addWidget(QLabel("Grid Density (Boxes):"))
        self.grid_density_spin = QSpinBox()
        self.grid_density_spin.setRange(2, 100)
        self.grid_density_spin.setValue(self.config.get("grid_density", 10))
        self.grid_density_spin.valueChanged.connect(self.sync_grid_from_ui)
        density_layout.addWidget(self.grid_density_spin)
        density_layout.addStretch()
        grid_layout.addLayout(density_layout)
        
        # System Prompt Section
        sys_group = QGroupBox("🤖 AI Instructions (System Command)")
        sys_layout = QVBoxLayout(sys_group)
        self.system_prompt_edit = QTextEdit()
        
        from omg.llm.prompts import PromptTemplates
        current_sys = self.config.get("system_prompt", "").strip()
        if not current_sys:
            current_sys = PromptTemplates.get_system_prompt()
            
        self.system_prompt_edit.setPlainText(current_sys)
        self.system_prompt_edit.setPlaceholderText("Enter extra instructions for the AI here...")
        self.system_prompt_edit.setFixedHeight(250) 
        sys_layout.addWidget(self.system_prompt_edit)
        grid_layout.addWidget(sys_group)

        parent_layout.addRow(grid_group)
        
        # Final syncs
        self.sync_grid_from_ui()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, self.auto_sync_model)

    def auto_sync_model(self):
        """Checks LM Studio for the currently loaded model and updates the UI."""
        server_url = self.url_input.text()
        from omg.llm.client import LLMClient
        client = LLMClient(base_url=server_url)
        
        active_model = client.get_active_model()
        if active_model:
            self.model_input.setText(active_model)
            self.config["model_id"] = active_model
            # Update Chat indicator too
            if hasattr(self, 'model_label'):
                self.model_label.setText(f"🤖 Model: {active_model}")
            self.update_log(f"✅ Auto-Sync: Detected model '{active_model}' in LM Studio.")
            self.save_tasks() # Persist the change
        else:
            self.update_log("⚠️ Sync: Could not find any loaded models in LM Studio. Is the server running?")

    def sync_grid_from_ui(self):
        enabled = self.grid_check.isChecked()
        opacity = self.grid_opacity_slider.value()
        density = self.grid_density_spin.value() # Get density
        
        # Update config state
        self.config["grid_enabled"] = enabled
        self.config["grid_opacity"] = opacity
        self.config["grid_density"] = density # Update config
        
        # Update Overlay Display
        self.grid_overlay.update_settings(
            enabled=enabled,
            opacity=opacity,
            density=density, # Pass density
            color_hex="#3498DB"
        )

    def create_logs_section(self, parent_layout):
        log_group = QGroupBox("📜 System Activity Logs")
        log_layout = QVBoxLayout(log_group)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(250) # Set reasonable fixed height for bottom of settings
        self.log_area.setStyleSheet("""
            background-color: #2C3E50; 
            color: #ECF0F1; 
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            border: 1px solid #34495E;
            border-radius: 4px;
        """)
        log_layout.addWidget(self.log_area)
        parent_layout.addRow(log_group)

    # def create_logs_tab(self):  # Removed standalone tab

    # Bot Logic
    def show_bot_dialog(self, bot_card=None):
        data = bot_card.bot_data if bot_card else None
        dialog = BotDialog(self, data)
        if dialog.exec():
            new_data = dialog.get_data()
            if bot_card:
                bot_card.bot_data.update(new_data)
                bot_card.name_label.setText(new_data["name"])
                bot_card.type_label.setText(f"{new_data['type']} ({new_data['url']})" if new_data['url'] else new_data['type'])
            else:
                new_data["linked_prompts"] = []
                self.add_bot_card(new_data)
            self.save_bots()

    def add_bot_card(self, data):
        card = BotCard(data)
        card.edit_clicked.connect(self.show_bot_dialog)
        card.delete_clicked.connect(self.delete_bot)
        card.open_clicked.connect(self.open_bot_interface)
        card.open_overlay_clicked.connect(self.toggle_bot_overlay)
        self.bot_layout.insertWidget(self.bot_layout.count() - 1, card)
        self.bot_cards.append(card)

    def delete_bot(self, card):
        from PyQt6.QtWidgets import QMessageBox
        if QMessageBox.question(self, "Delete Bot", f"Are you sure you want to delete '{card.bot_data['name']}'?", 
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.bot_cards.remove(card)
            card.setParent(None)
            card.deleteLater()
            self.save_bots()

    def open_bot_interface(self, card):
        dialog = BotInterfaceDialog(card, self)
        dialog.exec()

    def save_bots(self):
        data = [c.bot_data for c in self.bot_cards]
        with open(self.bots_file, 'w') as f:
            json.dump(data, f)

    def load_bots(self):
        if os.path.exists(self.bots_file):
            try:
                with open(self.bots_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        self.add_bot_card(item)
            except: pass

    # OCR Bot Logic
    def show_ocr_bot_dialog(self, bot_card=None):
        data = bot_card.bot_data if bot_card else None
        dialog = BotDialog(self, data)
        if dialog.exec():
            new_data = dialog.get_data()
            new_data["is_ocr"] = True
            if bot_card:
                bot_card.bot_data.update(new_data)
                bot_card.name_label.setText(new_data["name"])
                bot_card.type_label.setText(f"{new_data['type']} ({new_data['url']})" if new_data['url'] else new_data['type'])
            else:
                new_data["linked_prompts"] = []
                self.add_ocr_bot_card(new_data)
            self.save_ocr_bots()

    def add_ocr_bot_card(self, data):
        card = BotCard(data)
        card.edit_clicked.connect(self.show_ocr_bot_dialog)
        card.delete_clicked.connect(self.delete_ocr_bot)
        card.open_clicked.connect(self.open_bot_interface)
        card.open_overlay_clicked.connect(self.toggle_ocr_bot_overlay)
        self.ocr_bot_layout.insertWidget(self.ocr_bot_layout.count() - 1, card)
        self.ocr_bot_cards.append(card)

    def delete_ocr_bot(self, card):
        from PyQt6.QtWidgets import QMessageBox
        if QMessageBox.question(self, "Delete OCR Bot", f"Are you sure you want to delete '{card.bot_data['name']}'?", 
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.ocr_bot_cards.remove(card)
            card.setParent(None)
            card.deleteLater()
            self.save_ocr_bots()

    def save_ocr_bots(self):
        data = [c.bot_data for c in self.ocr_bot_cards]
        with open(self.bots_ocr_file, 'w') as f:
            json.dump(data, f)

    def load_ocr_bots(self):
        if os.path.exists(self.bots_ocr_file):
            try:
                with open(self.bots_ocr_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        item["is_ocr"] = True
                        self.add_ocr_bot_card(item)
            except: pass

    # Functions
    def show_prompt_dialog(self):
        dialog = PromptDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data["name"]:
                self.add_task_card(data["name"], data["type"])
                self.save_tasks()

    def add_task_card(self, name, prompt_type, saved_prompt=""):
        card = TaskCard(name, prompt_type)
        if saved_prompt:
            card.prompt_edit.setPlainText(saved_prompt)
        card.delete_clicked.connect(self.delete_task) # New
        card.edit_clicked.connect(self.edit_task)     # New
        
        # Insert before the spacer
        self.tasks_layout.insertWidget(self.tasks_layout.count() - 1, card)
        self.task_cards.append(card)

    def delete_task(self, card):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{card.name}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.task_cards.remove(card)
            card.setParent(None)
            card.deleteLater()
            self.save_tasks()
            self.update_log(f"🗑️ Task deleted: {card.name}")

    def edit_task(self, card):
        dialog = PromptDialog(self, name=card.name, prompt_type=card.prompt_type)
        if dialog.exec():
            data = dialog.get_data()
            card.name = data["name"]
            card.prompt_type = data["type"]
            card.name_label.setText(card.name)
            card.type_label.setText(f"({card.prompt_type.capitalize()})")
            card.prompt_edit.setPlaceholderText(f"Enter {card.prompt_type} prompt here...")
            self.save_tasks()
            self.update_log(f"✏️ Task updated: {card.name}")

    def run_task(self, task_data, bot_context=None):
        # Stop any existing worker
        self.stop_agent()
        
        # 1. Update global config from settings
        self.config["base_url"] = self.url_input.text()
        self.config["model_id"] = self.model_input.text()
        self.config["temperature"] = self.temp_spin.value()
        self.config["max_history"] = self.history_spin.value()
        self.config["action_delay"] = self.delay_spin.value()
        self.config["system_prompt"] = self.system_prompt_edit.toPlainText()
        self.config["grid_to_ai"] = self.grid_to_ai_check.isChecked()
        
        # Override memory for specific bot if needed
        if bot_context and not bot_context.get("use_default_memory", True):
            self.config["max_history"] = bot_context.get("memory_limit", 3)
            self.update_log(f"🧠 Bot-Specific Memory: {self.config['max_history']} steps")
        
        bot_name = bot_context.get("name") if bot_context else "General Agent"
        self.update_log(f"🚀 Starting Bot: {bot_name} | Task: {task_data['name']}")
        
        # 2. Handle Bot-Specific Actions (e.g., Open URL)
        if bot_context and bot_context.get("type") == "Website" and bot_context.get("url"):
            import webbrowser
            self.update_log(f"🌍 Navigating to: {bot_context['url']}")
            webbrowser.open(bot_context["url"])
            time.sleep(2) # Give browser a moment to appear
        
        # 3. Initialize Worker
        is_ocr = (self.current_bot_type == "ocr")
        self.worker = AgentWorker(self.config, is_ocr=is_ocr)
        if is_ocr:
            self.update_log("👁️ OCR Mode Active: The bot will use text-based targeting.")
            
        self.worker.setup_task(
            task_data["prompt"], 
            system_prompt=self.config.get("system_prompt"),
            initial_prompt=None # Handled by setup_task logic if needed
        )
        self.worker.log_update.connect(self.update_log)
        self.worker.status_update.connect(self.overlay.update_status)
        self.worker.finished.connect(self.on_finished)
        
        # 4. Contextual Prompt Injection
        system_prompt = task_data["prompt"] if task_data["type"] == "system" else None
        
        # Add Bot context to system prompt if available
        if bot_context:
            context_str = f"\n\nBOT CONTEXT: You are operating as the '{bot_context['name']}' bot."
            context_str += f"\nEnvironment Type: {bot_context['type']}"
            if bot_context.get("url"):
                context_str += f"\nTarget Website: {bot_context['url']}"
            
            if system_prompt:
                system_prompt += context_str
            else:
                system_prompt = context_str

        initial_prompt = task_data["prompt"] if task_data["type"] == "initial" else None
        
        # Minimize main window to clear the desktop for the AI BEFORE starting
        self.showMinimized()
        QApplication.processEvents() # Ensure UI updates
        time.sleep(0.5) # Wait for minimize animation
        
        self.worker.start()
        
        # Update Overlay UI state
        if hasattr(self, 'overlay'):
            self.overlay.title_label.setText(f"🤖 {bot_name}")
            self.overlay.set_running_state(True)
        
        self.overlay.show()
        # self.show_overlay_btn.setChecked(True) # Removed

    def stop_agent(self):
        if self.worker:
            self.worker.stop()
            self.worker = None # Clear worker after stop
            self.update_log("🛑 Stopping Agent worker...")
        if hasattr(self, 'overlay'):
            self.overlay.set_running_state(False)

    def toggle_bot_overlay(self, card):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            # Set context
            self.current_bot_data = card.bot_data
            self.current_bot_type = "bot"
            bot_name = self.current_bot_data.get("name", "Bot")
            self.overlay.title_label.setText(f"🤖 {bot_name}")
            self.overlay.show()
            self.update_log(f"📟 Overlay opened for: {bot_name}")

    def toggle_ocr_bot_overlay(self, card):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            # Set context
            self.current_bot_data = card.bot_data
            self.current_bot_type = "ocr"
            bot_name = self.current_bot_data.get("name", "OCR Bot")
            self.overlay.title_label.setText(f"👁️ {bot_name}")
            self.overlay.show()
            self.update_log(f"📟 OCR Overlay opened for: {bot_name}")


    def toggle_pause(self):
        if self.worker:
            paused = not self.worker.paused
            self.worker.set_paused(paused)
            self.update_log("⏸ Paused" if paused else "▶ Resumed")
        else:
            # If idle, try to start the first linked prompt
            if not self.current_bot_data:
                self.update_log("⚠️ No active bot selected. Please click 'Run Bot' on a card.")
                return
                
            prompts = self.current_bot_data.get("linked_prompts", [])
            if not prompts:
                self.update_log(f"⚠️ No prompts linked to '{self.current_bot_data['name']}'. Please set it up first!")
                return
                
            # Find the actual prompt data for the first linked name
            p_name = prompts[0]
            prompt_card = next((c for c in self.task_cards if c.name == p_name), None)
            if prompt_card:
                task_data = {
                    "name": prompt_card.name,
                    "type": prompt_card.prompt_type,
                    "prompt": prompt_card.prompt_edit.toPlainText()
                }
                self.run_task(task_data, bot_context=self.current_bot_data)
            else:
                self.update_log(f"⚠️ Could not find prompt data for '{p_name}'. It might have been deleted.")

    def update_log(self, text):
        self.log_area.append(f"[{time.strftime('%H:%M:%S')}] {text}")

    def send_chat_message(self):
        msg = self.chat_input.text().strip()
        if not msg and not self.pending_image_path:
            return
            
        self.chat_input.clear()
        
        # Start Loading State
        self.chat_loading_label.show()
        self.send_chat_btn.setEnabled(False)
        self.send_chat_btn.setText("⏳")
        self.chat_input.setEnabled(False)
        
        display_msg = msg
        has_image = bool(self.pending_image_path)
        if has_image:
            display_msg = f"🖼️ [Image Attached] {msg}"
            
        self.add_chat_bubble(display_msg, "user")
        
        try:
            from omg.llm.prompts import PromptTemplates
            current_session = self.session_manager.get_current()
            
            chat_sys_prompt = self.chat_system_prompt_edit.toPlainText().strip()
            if not chat_sys_prompt:
                chat_sys_prompt = "You are OMG, a helpful AI assistant. Answer the user's questions clearly and concisely."

            if has_image:
                # --- Image path: load the attached file ---
                from PIL import Image
                img = Image.open(self.pending_image_path).convert("RGB")
                self.pending_image_path = None
                self.attach_btn.setStyleSheet("border: none; font-size: 18px; color: #7F8C8D;")
                
                img_resized = self.chat_preprocessor.resize_for_vision_model(img)
                img_b64 = self.chat_preprocessor.encode_to_base64_string(img_resized)
                
                messages = PromptTemplates.build_payload(
                    img_b64,
                    f"[Image Attached]: {msg}",
                    current_session.history,
                    system_prompt=chat_sys_prompt,
                    is_chat=True
                )
            else:
                # --- Text-only path: no screenshot, no image ---
                messages = [{"role": "system", "content": chat_sys_prompt}]
                for entry in current_session.history:
                    messages.append({"role": entry["role"], "content": entry["content"]})
                messages.append({"role": "user", "content": msg})
            
            # Start Streaming Worker
            from omg.ui.worker import ChatWorker
            self.current_bubble = None
            self.chat_worker = ChatWorker(
                self.chat_client,
                self.config.get("model_id", "qwen2-vl-7b-instruct"),
                messages,
                temperature=0.7
            )
            self.chat_worker.chunk_received.connect(self.on_chat_chunk)
            self.chat_worker.finished.connect(lambda full_text: self.on_chat_finished(msg, full_text))
            self.chat_worker.error.connect(self.on_chat_error)
            self.chat_worker.start()
                
        except Exception as e:
            self.on_chat_error(str(e))


    def on_chat_chunk(self, chunk):
        if not self.current_bubble:
            from omg.ui.chat_bubble import ChatBubble
            self.current_bubble = ChatBubble("", "assistant")
            self.chat_v_layout.insertWidget(self.chat_v_layout.count() - 1, self.current_bubble)
            
        self.current_bubble.update_text(self.current_bubble.text + chunk)
        # Scroll to bottom
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    def on_chat_finished(self, user_msg, full_text):
        self.chat_loading_label.hide()
        self.send_chat_btn.setEnabled(True)
        self.send_chat_btn.setText("⬆")
        self.chat_input.setEnabled(True)
        self.chat_input.setFocus()
        
        # Update Session Data
        current_session = self.session_manager.get_current()
        current_session.add_message("user", user_msg)
        current_session.add_message("assistant", full_text)
        
        # Auto naming
        if len(current_session.history) <= 2:
            current_session.name = user_msg[:25] + ("..." if len(user_msg) > 25 else "")
        
        self.update_session_list()
        self.save_sessions()

    def on_chat_error(self, error_msg):
        self.chat_loading_label.hide()
        self.send_chat_btn.setEnabled(True)
        self.send_chat_btn.setText("⬆")
        self.chat_input.setEnabled(True)
        self.add_chat_bubble(f"Error: {error_msg}", "assistant")

    def add_chat_bubble(self, text, sender):
        from omg.ui.chat_bubble import ChatBubble
        bubble = ChatBubble(text, sender)
        # Add before the spacer
        self.chat_v_layout.insertWidget(self.chat_v_layout.count() - 1, bubble)
        # Scroll to bottom
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    def show_chat_context_menu(self, pos):
        item = self.session_list.itemAt(pos)
        if not item:
            return
            
        from PyQt6.QtWidgets import QMenu, QInputDialog
        menu = QMenu(self)
        rename_action = menu.addAction("✏️ Rename")
        delete_action = menu.addAction("🗑️ Delete")
        
        action = menu.exec(self.session_list.mapToGlobal(pos))
        
        index = self.session_list.row(item)
        if action == rename_action:
            new_name, ok = QInputDialog.getText(self, "Rename Chat", "Enter new name:", text=item.text())
            if ok and new_name:
                self.session_manager.sessions[index].name = new_name
                self.update_session_list()
                self.save_sessions()
        elif action == delete_action:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "Confirm Delete", "Delete this chat session?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.session_manager.sessions.pop(index)
                if not self.session_manager.sessions:
                    self.session_manager.add_session()
                self.session_manager.current_index = 0
                self.update_session_list()
                self.on_session_clicked(self.session_list.item(0))
                self.save_sessions()

    def start_new_chat(self):
        new_sess = self.session_manager.add_session()
        self.update_session_list()
        self.on_session_clicked(self.session_list.item(self.session_list.count() - 1))

    def on_session_clicked(self, item):
        index = self.session_list.row(item)
        self.session_manager.set_current(index)
        self.clear_chat_ui()
        for msg in self.session_manager.get_current().history:
            self.add_chat_bubble(msg["content"], msg["role"])

    def clear_chat_ui(self):
        while self.chat_v_layout.count() > 1:
            child = self.chat_v_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_session_list(self):
        self.session_list.clear()
        for sess in self.session_manager.sessions:
            self.session_list.addItem(sess.name)
        self.session_list.setCurrentRow(self.session_manager.current_index)

    def on_attach_clicked(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Attach Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.pending_image_path = file_path
            self.attach_btn.setStyleSheet("background-color: #F1C40F;") # Highlight button
            self.update_log(f"📎 Attached Image: {os.path.basename(file_path)}")

    def save_sessions(self):
        self.session_manager.save_to_file(self.session_file)

    def load_sessions(self):
        self.session_manager.load_from_file(self.session_file)
        # Wait for UI to be ready before updating list

    def on_finished(self, msg):
        self.update_log(f"✅ {msg}")
        self.worker = None # Clear worker when finished naturally
        for c in self.task_cards:
            c.reset_controls()

    def save_tasks(self):
        data = []
        for card in self.task_cards:
            data.append({
                "name": card.name,
                "type": card.prompt_type,
                "prompt": card.prompt_edit.toPlainText()
            })
        
        # Update settings config before saving
        self.config["base_url"] = self.url_input.text()
        self.config["model_id"] = self.model_input.text()
        self.config["temperature"] = self.temp_spin.value()
        self.config["max_history"] = self.history_spin.value()
        self.config["action_delay"] = self.delay_spin.value()
        self.config["permissions_granted"] = self.perm_check.isChecked()
        self.config["grid_enabled"] = self.grid_check.isChecked()
        self.config["grid_opacity"] = self.grid_opacity_slider.value()
        self.config["grid_density"] = self.grid_density_spin.value()
        self.config["grid_to_ai"] = self.grid_to_ai_check.isChecked()
        self.config["system_prompt"] = self.system_prompt_edit.toPlainText()
        self.config["chat_system_prompt"] = self.chat_system_prompt_edit.toPlainText()

        with open(self.config_file, 'w') as f:
            json.dump({"tasks": data, "settings": self.config}, f)
            
    def load_tasks(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    content = json.load(f)
                    # Handle legacy format vs new format
                    if isinstance(content, list):
                        task_data = content
                        settings_data = {}
                    else:
                        task_data = content.get("tasks", [])
                        settings_data = content.get("settings", {})
                    
                    if settings_data:
                        self.config.update(settings_data)
                        # Sync UI with loaded settings
                        self.url_input.setText(self.config.get("base_url", "http://localhost:1234/v1"))
                        self.model_input.setText(self.config.get("model_id", "qwen2-vl-7b-instruct"))
                        self.temp_spin.setValue(self.config.get("temperature", 0.2))
                        self.history_spin.setValue(self.config.get("max_history", 3))
                        self.delay_spin.setValue(self.config.get("action_delay", 1.5))
                        if hasattr(self, 'perm_check'):
                            self.perm_check.setChecked(self.config.get("permissions_granted", False))
                        
                        if hasattr(self, 'grid_check'):
                            self.grid_check.setChecked(self.config.get("grid_enabled", False))
                        if hasattr(self, 'grid_opacity_slider'):
                            self.grid_opacity_slider.setValue(self.config.get("grid_opacity", 50))
                        if hasattr(self, 'grid_density_spin'):
                            self.grid_density_spin.setValue(self.config.get("grid_density", 10))
                        if hasattr(self, 'grid_to_ai_check'):
                            self.grid_to_ai_check.setChecked(self.config.get("grid_to_ai", False))
                        if hasattr(self, 'system_prompt_edit'):
                            loaded_sys = self.config.get("system_prompt", "").strip()
                            if not loaded_sys:
                                from omg.llm.prompts import PromptTemplates
                                loaded_sys = PromptTemplates.get_system_prompt()
                            self.system_prompt_edit.setPlainText(loaded_sys)
                        
                        if hasattr(self, 'chat_system_prompt_edit'):
                            loaded_chat_sys = self.config.get("chat_system_prompt", "").strip()
                            # Auto-migrate: detect stale visual-AI prompts and replace them
                            stale_markers = ["POWERFUL VISUAL AI", "What's on your screen", "VISUAL AI", "screen or images"]
                            is_stale = not loaded_chat_sys or any(m in loaded_chat_sys for m in stale_markers)
                            if is_stale:
                                loaded_chat_sys = "You are OMG, a helpful and knowledgeable AI assistant. Answer the user's questions clearly, concisely, and helpfully."
                                self.config["chat_system_prompt"] = loaded_chat_sys
                            self.chat_system_prompt_edit.setPlainText(loaded_chat_sys)

                    for item in task_data:
                        self.add_task_card(item["name"], item["type"], item.get("prompt", ""))
            except Exception as e:
                self.update_log(f"⚠️ Error loading config: {e}")
                
    def closeEvent(self, event):
        self.save_tasks()
        event.accept()
