class SequentialPool:
    def __init__(self, processes=None, initializer=None, initargs=()):
        self.initializer = initializer
        self.initargs = initargs

    def __enter__(self):
        if self.initializer:
            self.initializer(*self.initargs)
        return self

    def __exit__(self, *args):
        pass

    def map(self, func, iterable):
        return [func(item) for item in iterable]