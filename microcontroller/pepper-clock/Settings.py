from uos import remove

FILE = "./settings.csv"


class Settings:
    def __init__(self, eco_mode=b"0", offset_hour=b"0", offset_minute=b"0"):
        self.eco_mode = eco_mode
        self.offset_hour = offset_hour
        self.offset_minute = offset_minute

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.eco_mode, self.offset_hour, self.offset_minute]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                content = f.read().split(b",")

            if len(content) == 3:
                self.eco_mode, self.offset_hour, self.offset_minute = content

            if not self.is_valid():
                self.remove()
        except OSError as e:
            # File not found
            if e.args[0] == 2:
                self.write()

        return self

    def remove(self):
        try:
            remove(FILE)
        except OSError:
            pass

        self.eco_mode = True

    def is_valid(self):
        # Ensure the credentials are entered as bytes
        if not isinstance(self.eco_mode, bytes):
            return False
        if not isinstance(self.offset_hour, bytes):
            return False
        if not isinstance(self.offset_minute, bytes):
            return False

        return True
