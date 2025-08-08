class Return(Exception):
    def __init__(self, value: object):
        self.value = value
