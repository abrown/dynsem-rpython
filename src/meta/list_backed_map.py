# So that you can still run this module under standard CPython...
try:
    from rpython.rlib.jit import unroll_safe, hint, elidable
except ImportError:
    def hint(x, **kwds):
        return x


    def unroll_safe(func):
        return func


    def elidable(func):
        return func


class ListBackedMap:
    def __init__(self):
        self.names = {}
        self.values = []

    @elidable
    def locate(self, name):
        if name not in self.names:
            index = len(self.names)
            self.names[name] = index
            if index >= len(self.values):
                self.values.append(None)
        return self.names[name]

    @unroll_safe
    def get(self, index):
        return self.values[index]

    @unroll_safe
    def put(self, index, value):
        num_values = len(self.values)
        if index > num_values:
            raise IndexError("index is more than one offset away from values array")
        if index == num_values:
            self.values.append(value)
        else:
            self.values[index] = value

    # helper method for tests, use separate calls instead
    def locate_and_get(self, name):
        index = self.locate(name)
        return self.get(index)

    # helper method for tests, use separate calls instead
    def locate_and_put(self, name, value):
        index = self.locate(name)
        self.put(index, value)
        return index
