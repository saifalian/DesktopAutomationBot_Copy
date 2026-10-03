import os

class Settings:
    # LM Studio API Settings
    BASE_URL = "http://localhost:1234/v1"
    MODEL_ID = "qwen2-vl-7b-instruct"  # Default, can be changed in UI
    TEMPERATURE = 0.2
    
    # Agent Settings
    MAX_HISTORY_STEPS = 3  # Default short memory
    ACTION_DELAY = 1.5      # Seconds between actions
    
    # UI Settings
    APP_NAME = "OMG"
    WINDOW_TITLE = "OMG: Autonomous Visual AI Agent"
    
    # Grid Layer Settings
    GRID_ENABLED = False
    GRID_OPACITY = 50 # 0-100
    GRID_DENSITY = 10 # Number of boxes per axis
    GRID_COLOR = "#3498DB"
    GRID_TO_AI = False # Whether to send the grid in the screenshot to the model
    
    SYSTEM_PROMPT = "" # Custom override
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    
    @classmethod
    def ensure_dirs(cls):
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)

Settings.ensure_dirs()
