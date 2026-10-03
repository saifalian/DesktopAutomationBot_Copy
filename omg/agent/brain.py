import time
import logging
import os
from datetime import datetime
from PIL import Image
from omg.vision.screenshot import ScreenShotter
from omg.vision.preprocess import ImagePreprocessor
from omg.llm.client import LLMClient
from omg.llm.prompts import PromptTemplates
from omg.agent.memory import ShortMemory
from omg.actions.mouse import MouseActions, KeyboardActions
from omg.vision.ocr import OCRAngine

class AgentBrain:
    def __init__(self, config=None):
        self.config = config or {}
        self.screenshotter = ScreenShotter()
        self.preprocessor = ImagePreprocessor()
        self.llm_client = LLMClient(
            base_url=self.config.get("base_url", "http://localhost:1234/v1"),
            api_key=self.config.get("api_key", "lm-studio")
        )
        self.memory = ShortMemory(max_steps=self.config.get("max_history", 3))
        self.running = False
        self.paused = False
        self.current_task = ""
        self.system_prompt = None
        self.initial_prompt = None
        self.screen_w, self.screen_h = self.screenshotter.get_screen_size()
        self.ocr_engine = OCRAngine()
        self.last_ocr_results = []
        self.is_ocr_mode = False
        
    def set_task(self, task, system_prompt=None, initial_prompt=None):
        self.current_task = task
        self.system_prompt = system_prompt
        self.initial_prompt = initial_prompt
        self.memory.clear()

    def run_cycle(self):
        """Executes one step of the (See -> Think -> Act) loop."""
        if self.paused:
            return "Paused"

        # 1. See: Capture screen
        img, path = self.screenshotter.capture(
            draw_grid=self.config.get("grid_to_ai", False),
            grid_density=self.config.get("grid_density", 10)
        )
        img_resized = self.preprocessor.resize_for_vision_model(img)
        img_b64 = self.preprocessor.encode_to_base64_string(img_resized)

        # 2. Think: Build payload and ask LLM
        history = self.memory.get_history()
        
        if self.is_ocr_mode:
            # Add OCR Step
            self.last_ocr_results = self.ocr_engine.extract_text_with_positions(img)
            ocr_text_summary = "\n".join([f"'{r['text']}' at {r['center']}" for r in self.last_ocr_results[:50]]) # Limit for context
            messages = PromptTemplates.build_ocr_payload(
                img_b64,
                self.current_task,
                ocr_text_summary,
                history=[], # OCR Mode works best as single-shot to avoid LM Studio history errors
                system_prompt=self.system_prompt,
                initial_prompt=self.initial_prompt,
                permissions_granted=self.config.get("permissions_granted", True),
                screen_size=(self.screen_w, self.screen_h)
            )
        else:
            messages = PromptTemplates.build_payload(
                img_b64, 
                self.current_task, 
                history, 
                system_prompt=self.system_prompt,
                initial_prompt=self.initial_prompt,
                permissions_granted=self.config.get("permissions_granted", True),
                screen_size=(self.screen_w, self.screen_h)
            )

        response = self.llm_client.ask(
            model=self.config.get("model_id", "qwen2-vl-7b-instruct"),
            messages=messages,
            temperature=self.config.get("temperature", 0.2)
        )

        if "error" in response:
            return f"Error: {response['error']}"

        # 3. Act: Execute action
        action_result = self._execute_action(response)
        
        # 4. Remember: Update short memory
        self.memory.add_turn("assistant", f"Thought: {response.get('thought')} | Action: {response.get('action')}")
        
        return response

    def _execute_action(self, response):
        """Map model coordinates and trigger system events."""
        action = response.get("action", "").lower()
        thought = response.get("thought", "")
        reason = response.get("reason", "")
        
        # Coordinate Denormalization (pct to pixels)
        x_pct = response.get("x")
        y_pct = response.get("y")
        
        target_x, target_y = None, None

        if action in ["click_text", "double_click_text"]:
            target_text = response.get("text")
            if target_text:
                coords = self.ocr_engine.find_text_coordinates(target_text, self.last_ocr_results)
                if coords:
                    target_x, target_y = coords
                    logging.info(f"📍 OCR Match Found: '{target_text}' at {coords}")
                else:
                    logging.warning(f"❌ OCR Match Failed for: '{target_text}'")
                    return "Action Failed: Text not found"
        
        if target_x is None and x_pct is not None:
            # Standard Percentage Mapping if pct provided
            # SAFETY CHECK: If the model outputs raw pixels (>100) instead of percentages,
            # we attempt to auto-correct by treating them as absolute values.
            if x_pct > 100 or y_pct > 100:
                logging.warning(f"⚠️ Model Hallucination: Received coordinates > 100 ({x_pct}, {y_pct}). Attempting auto-correction.")
                if x_pct > self.screen_w or y_pct > self.screen_h:
                    # Clamp if they are completely impossible
                    target_x = min(self.screen_w, max(0, int(x_pct)))
                    target_y = min(self.screen_h, max(0, int(y_pct)))
                    logging.warning(f"🚨 Clamping impossible coordinates to screen bounds: ({target_x}, {target_y})")
                else:
                    # Treat as absolute pixels
                    target_x = int(x_pct)
                    target_y = int(y_pct)
                    logging.info(f"🔄 Interpreting ({x_pct}, {y_pct}) as absolute pixels.")
            else:
                target_x = int(x_pct * self.screen_w / 100)
                target_y = int(y_pct * self.screen_h / 100)
        
        if target_x is None:
            # Fallback for other actions
            target_x, target_y = 0, 0
        
        logging.info(f"THOUGHT: {thought}")
        logging.info(f"ACTION: {action} at ({target_x}, {target_y}) [Reason: {reason}]")

        if action in ["click", "click_text"]:
            MouseActions.click(target_x, target_y)
        elif action in ["double_click", "double_click_text"]:
            MouseActions.double_click(target_x, target_y)
        elif action == "type":
            text = response.get("text", "")
            KeyboardActions.type_text(text)
        elif action == "scroll":
            MouseActions.scroll(500)
        elif action == "done":
            self.running = False
            return "Task Complete"
        
        return "Step Executed"
