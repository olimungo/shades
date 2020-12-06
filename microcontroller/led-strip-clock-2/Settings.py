from uos import remove

FILE = "./settings.csv"

class Settings:
    def __init__(self, net_id=b"0", group=b"", color=b"0000ff"):
        self.net_id = net_id
        self.group = group
        self.color = color

    def write(self):
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.net_id, self.group, self.color]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                contents = f.read().split(b",")

            if len(contents) == 3:
                self.net_id, self.group, self.color = contents

            if not self.is_valid():
                remove()
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

        self.net_id = self.group = self.color = None

    def is_valid(self):
        # Ensure the credentials are entered as bytes
        if not isinstance(self.net_id, bytes):
            return False
        if not isinstance(self.group, bytes):
            return False
        if not isinstance(self.color, bytes):
            return False

        return True
