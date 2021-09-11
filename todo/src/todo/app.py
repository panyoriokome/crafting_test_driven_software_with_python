import functools

class TODOApp:
    def __init__(self, io=(input, functools.partial(print, end=""))):
        self._in, self.out = io