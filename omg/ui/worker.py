from PyQt6.QtCore import QThread, pyqtSignal
from omg.agent.brain import AgentBrain
import time

class AgentWorker(QThread):
    finished = pyqtSignal(str)
    status_update = pyqtSignal(dict)
    log_update = pyqtSignal(str)

    def __init__(self, config, is_ocr=False):
        super().__init__()
        self.config = config
        self.brain = AgentBrain(config=config)
        self.brain.is_ocr_mode = is_ocr
        self.running = False
        self.paused = False

    def setup_task(self, task, system_prompt=None, initial_prompt=None):
        self.brain.set_task(task, system_prompt, initial_prompt)

    def run(self):
        # Reset screenshotter handle so it auto-re-initializes on THIS thread
        if hasattr(self.brain, 'screenshotter') and self.brain.screenshotter:
            self.brain.screenshotter._sct = None
            
        self.running = True
        self.brain.running = True
        
        while self.running and self.brain.running:
            if self.paused:
                time.sleep(0.5)
                continue
                
            try:
                result = self.brain.run_cycle()
                
                if isinstance(result, dict):
                    thought = result.get('thought', '')
                    action = result.get('action', '')
                    x = result.get('x')
                    y = result.get('y')
                    text = result.get('text')
                    
                    self.status_update.emit(result)
                    if thought:
                        self.log_update.emit(f"🧠 Thought: {thought}")
                    
                    act_msg = f"🚀 Action: {action}"
                    if x is not None and y is not None:
                        act_msg += f" at ({x}%, {y}%)"
                    elif text:
                        act_msg += f" with text: '{text}'"
                        
                    self.log_update.emit(act_msg)
                else:
                    self.log_update.emit(f"⚠️ {str(result)}")
                
                # Minimum delay between steps
                time.sleep(self.config.get("action_delay", 1.5))
                
            except Exception as e:
                self.log_update.emit(f"Worker Error: {str(e)}")
                self.running = False
                break
                
        self.finished.emit("Task Finished")

    def stop(self):
        self.running = False
        self.brain.running = False
        
    def set_paused(self, paused):
        self.paused = paused
        self.brain.paused = paused

class ChatWorker(QThread):
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client, model, messages, temperature=0.7):
        super().__init__()
        self.client = client
        self.model = model
        self.messages = messages
        self.temperature = temperature
        self.full_response = ""

    def run(self):
        try:
            for chunk in self.client.ask_stream(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature
            ):
                self.full_response += chunk
                self.chunk_received.emit(chunk)
            
            self.finished.emit(self.full_response)
        except Exception as e:
            self.error.emit(str(e))
