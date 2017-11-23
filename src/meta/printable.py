class Printable:
    def to_string(self):
        return self.__class__.__name__  # by default just print the class name

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()