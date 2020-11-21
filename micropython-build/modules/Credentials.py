from uos import remove

FILE = "./creds.csv"

class Credentials:
    def __init__(self, essid=None, password=None):
        self.essid = essid
        self.password = password

    def write(self):
        """Write credentials to FILE if valid input found."""
        
        if self.is_valid():
            with open(FILE, "wb") as f:
                f.write(b",".join([self.essid, self.password]))

    def load(self):
        try:
            with open(FILE, "rb") as f:
                contents = f.read().split(b",")

            if len(contents) == 2:
                self.essid, self.password = contents

            if not self.is_valid():
                self.remove()
        except OSError:
            pass

        return self

    def remove(self):
        """
        1. Delete credentials file from disk.
        2. Set essid and password to None
        """
        
        try:
            remove(FILE)
        except OSError:
            pass

        self.essid = self.password = None

    def is_valid(self):
        # Ensure the credentials are entered as bytes
        if not isinstance(self.essid, bytes):
            return False
        if not isinstance(self.password, bytes):
            return False

        # Ensure credentials are not None or empty
        return all((self.essid, self.password))
