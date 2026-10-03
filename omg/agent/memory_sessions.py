import json
from collections import deque

class ChatSession:
    def __init__(self, name="New Chat"):
        self.name = name
        self.history = [] # list of {"role": "user", "content": "..."}

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def to_dict(self):
        return {"name": self.name, "history": self.history}

    @classmethod
    def from_dict(cls, data):
        session = cls(name=data.get("name", "New Chat"))
        session.history = data.get("history", [])
        return session

class SessionManager:
    def __init__(self):
        self.sessions = [ChatSession()]
        self.current_index = 0

    def add_session(self, name="New Chat"):
        new_sess = ChatSession(name=name)
        self.sessions.append(new_sess)
        self.current_index = len(self.sessions) - 1
        return new_sess

    def get_current(self):
        return self.sessions[self.current_index]

    def set_current(self, index):
        if 0 <= index < len(self.sessions):
            self.current_index = index

    def save_to_file(self, path):
        data = [s.to_dict() for s in self.sessions]
        with open(path, 'w') as f:
            json.dump(data, f)

    def load_from_file(self, path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self.sessions = [ChatSession.from_dict(d) for d in data]
                if not self.sessions:
                    self.sessions = [ChatSession()]
                self.current_index = 0
        except:
            self.sessions = [ChatSession()]
            self.current_index = 0
