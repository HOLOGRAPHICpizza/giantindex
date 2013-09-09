class _Comparison(object):
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value

class LessThan(Comparison):
    pass

class GreaterThan(Comparison):
    pass

class Contains(Comparison):
    pass

class StartsWith(Comparison):
    pass

