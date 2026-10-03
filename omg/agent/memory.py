from collections import deque
import json

class ShortMemory:
    def __init__(self, max_steps=5):
        self.history = deque(maxlen=max_steps)

    def add_turn(self, role, content):
        """Adds a message turn to the history."""
        self.history.append({"role": role, "content": content})

    def get_history(self):
        """Returns the list of messages in a format the model understands."""
        return list(self.history)

    def clear(self):
        """Clears the short-term memory."""
        self.history.clear()

    def serialize(self):
        """Returns the history as a JSON string for persistence."""
        return json.dumps(list(self.history))
        
    def set_max_steps(self, steps):
        """Dynamically updates the memory window size."""
        new_history = deque(list(self.history), maxlen=steps)
        self.history = new_history
