from pynput.keyboard import Key, Listener, KeyCode

class KeystrokeListener:
    def __init__(self):

        self.callbacks = {}

        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def addCallback(self, key, callback):
        self.callbacks[key] = callback

    def on_press(self, key):
        # try:
        #     print(f"{key.char} pressed")
        # except AttributeError:
        #     print(f"{key} pressed.")

        for dictKey, callback in self.callbacks.items():
            if (key == dictKey):
                callback(True)

    def on_release(self, key):
        for dictKey, callback in self.callbacks.items():
            if (key == dictKey):
                callback(False)


listener = KeystrokeListener()