class StringBuilder:
    def __init__(self):
        self.value = ""
    def append(self, value):
        self.value += str(value)
        return self
    def toString(self):
        return self.value