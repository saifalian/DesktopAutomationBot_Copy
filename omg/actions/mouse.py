import pyautogui
import time
import logging

# Disable Fail-Safe to allow clicking near screen corners (like the Close button)
pyautogui.FAILSAFE = False

class MouseActions:
    @staticmethod
    def _clamp(x, y):
        """Ensures coordinates stay just within screen boundaries."""
        width, height = pyautogui.size()
        return max(1, min(x, width-1)), max(1, min(y, height-1))

    @staticmethod
    def click(x, y, duration=0.2):
        """Moves to (x, y) and performs a click."""
        x, y = MouseActions._clamp(x, y)
        pyautogui.moveTo(x, y, duration=duration)
        pyautogui.click()
        logging.info(f"Clicked at ({x}, {y})")

    @staticmethod
    def double_click(x, y, duration=0.2):
        """Moves to (x, y) and performs a double-click."""
        x, y = MouseActions._clamp(x, y)
        pyautogui.moveTo(x, y, duration=duration)
        pyautogui.doubleClick()
        logging.info(f"Double-clicked at ({x}, {y})")

    @staticmethod
    def drag(x1, y1, x2, y2, duration=0.5):
        """Drags from (x1, y1) to (x2, y2)."""
        pyautogui.moveTo(x1, y1)
        pyautogui.dragTo(x2, y2, duration=duration)
        logging.info(f"Dragged from ({x1}, {y1}) to ({x2}, {y2})")

    @staticmethod
    def scroll(amount, direction="down"):
        """Scrolls the mouse wheel."""
        if direction == "up":
            pyautogui.scroll(amount)
        else:
            pyautogui.scroll(-amount)
        logging.info(f"Scrolled {direction} by {amount}")

class KeyboardActions:
    @staticmethod
    def type_text(text, interval=0.05):
        """Types a string of text."""
        pyautogui.write(text, interval=interval)
        logging.info(f"Typed text: {text}")

    @staticmethod
    def press_key(key):
        """Presses a single key (e.g. 'enter', 'esc')."""
        pyautogui.press(key)
        logging.info(f"Pressed key: {key}")

    @staticmethod
    def hotkey(*args):
        """Presses a combination of keys (e.g. 'ctrl', 'c')."""
        pyautogui.hotkey(*args)
        logging.info(f"Pressed hotkey: {args}")
