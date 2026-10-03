from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget, QFrame, QGroupBox, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt

class BotInterfaceDialog(QDialog):
    def __init__(self, bot_card, parent_dashboard):
        super().__init__(parent_dashboard)
        self.bot_card = bot_card
        self.dashboard = parent_dashboard
        self.bot_data = bot_card.bot_data
        
        self.setWindowTitle(f"Bot Dashboard: {self.bot_data['name']}")
        self.resize(500, 650) # Made taller for new section
        self.init_ui()

    def open_edit_dialog(self):
        # reuse dashboard logic
        self.dashboard.show_bot_dialog(self.bot_card)
        # Refresh current UI with new name/memory status
        self.setWindowTitle(f"Bot Dashboard: {self.bot_card.bot_data['name']}")
        self.refresh_ui()

    def refresh_ui(self):
        # Update the local bot_data reference as it might have been replaced
        self.bot_data = self.bot_card.bot_data
        
        # Clear ALL widgets in the main layout
        if self.layout():
            while self.layout().count():
                child = self.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        # Re-initialize UI elements using the existing layout if possible, 
        # but since init_ui creates a layout, we need to handle that.
        self.setup_ui_content()

    def init_ui(self):
        # Create common layout if not exists
        if not self.layout():
            QVBoxLayout(self)
        self.setup_ui_content()

    def setup_ui_content(self):
        main_layout = self.layout()
        
        # Info Header
        info_group = QGroupBox("Bot Details")
        info_layout = QVBoxLayout(info_group)
        
        type_label = QLabel(f"<b>Environment:</b> {self.bot_data['type']}")
        info_layout.addWidget(type_label)
        
        if self.bot_data.get("url"):
            url_label = QLabel(f"<b>Target URL:</b> {self.bot_data['url']}")
            info_layout.addWidget(url_label)
        
        main_layout.addWidget(info_group)
        
        # Memory Info Section
        mem_group = QGroupBox("Memory & Context Settings")
        mem_layout = QVBoxLayout(mem_group)
        
        is_default = self.bot_data.get("use_default_memory", True)
        if is_default:
            global_mem = self.dashboard.config.get("max_history", 3)
            mem_text = f"<b>Mode:</b> Using Global Settings ({global_mem} Steps)"
        else:
            custom_mem = self.bot_data.get("memory_limit", 3)
            mem_text = f"<b>Mode:</b> Custom Override ({custom_mem} Steps)"
            
        mem_status = QLabel(mem_text)
        mem_status.setStyleSheet("color: #3498DB; font-size: 12px;")
        mem_layout.addWidget(mem_status)
        
        # Add Edit Bot Button for easy access to memory settings
        self.edit_bot_btn = QPushButton("✏️ Edit Bot Settings (Memory, URL, Name)")
        self.edit_bot_btn.setStyleSheet("""
            background-color: #BDC3C7; color: #2C3E50; padding: 5px; 
            font-size: 11px; font-weight: bold; border-radius: 4px;
        """)
        self.edit_bot_btn.clicked.connect(self.open_edit_dialog)
        mem_layout.addWidget(self.edit_bot_btn)
        
        main_layout.addWidget(mem_group)
        
        # Prompts Section
        prompt_group = QGroupBox("Linked Prompts (AI Instructions)")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.link_btn = QPushButton("🔗 Link New Prompt to this Bot")
        self.link_btn.setStyleSheet("""
            background-color: #3498DB; color: white; padding: 10px; 
            font-weight: bold; border-radius: 5px;
        """)
        self.link_btn.clicked.connect(self.add_link)
        prompt_layout.addWidget(self.link_btn)
        
        # Scroll area for prompts
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.prompts_v_layout = QVBoxLayout(self.scroll_content)
        self.prompts_v_layout.addStretch()
        self.scroll.setWidget(self.scroll_content)
        prompt_layout.addWidget(self.scroll)
        
        main_layout.addWidget(prompt_group)
        
        # Footer
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn)
        
        self.refresh_prompts()

    def refresh_prompts(self):
        # Clear existing
        while self.prompts_v_layout.count() > 1:
            child = self.prompts_v_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        linked_names = self.bot_data.get("linked_prompts", [])
        for name in linked_names:
            # Find matching prompt from dashboard's task_cards
            prompt_card = next((c for c in self.dashboard.task_cards if c.name == name), None)
            
            p_frame = QFrame()
            p_frame.setStyleSheet("background-color: #F8F9F9; border: 1px solid #D5DBDB; border-radius: 8px;")
            p_layout = QHBoxLayout(p_frame)
            
            p_info = QLabel(f"<b>{name}</b>" + (f" ({prompt_card.prompt_type})" if prompt_card else ""))
            p_info.setStyleSheet("color: #2C3E50; border: none;") # High contrast dark text
            p_layout.addWidget(p_info)
            p_layout.addStretch()
            
            if prompt_card:
                run_btn = QPushButton("▶ Run")
                run_btn.setStyleSheet("background-color: #2ECC71; color: white; font-weight: bold; padding: 5px 15px;")
                run_btn.clicked.connect(lambda _, c=prompt_card: self.run_prompt(c))
                p_layout.addWidget(run_btn)
            
            unlink_btn = QPushButton("🗑️")
            unlink_btn.setToolTip("Unlink from Bot")
            unlink_btn.clicked.connect(lambda _, n=name: self.confirm_unlink(n))
            p_layout.addWidget(unlink_btn)
            
            self.prompts_v_layout.insertWidget(self.prompts_v_layout.count() - 1, p_frame)

    def add_link(self):
        all_prompt_names = [c.name for c in self.dashboard.task_cards]
        if not all_prompt_names:
            QMessageBox.warning(self, "No Prompts", "Go to the 'Prompts' tab to create a task first!")
            return
            
        name, ok = QInputDialog.getItem(self, "Link Prompt", "Select prompt to add:", all_prompt_names, 0, False)
        if ok and name:
            if name not in self.bot_data["linked_prompts"]:
                self.bot_data["linked_prompts"].append(name)
                self.refresh_prompts()
                self.dashboard.save_bots()

    def confirm_unlink(self, name):
        self.bot_data["linked_prompts"].remove(name)
        self.refresh_prompts()
        self.dashboard.save_bots()

    def run_prompt(self, card):
        self.dashboard.run_task(
            {"name": card.name, "type": card.prompt_type, "prompt": card.prompt_edit.toPlainText()},
            bot_context=self.bot_data
        )
        # Optional: hide dialog on run? 
        # self.hide() 
