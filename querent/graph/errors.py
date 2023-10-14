class InvalidURIException(Exception):
    def __init__(self, uri):
        self.uri = uri
        super().__init__(self.uri)


class PrefixNotFoundException(Exception):
    def __init__(self, prefix):
        self.prefix = prefix
        super().__init__(self.prefix)


class InvalidGraphNodeValueError(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(self.value)


class UnknownLiteralType(Exception):
    def __init__(self):
        super().__init__()


class InvalidParameter(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class SplitURIWithUnknownPrefix(Exception):
    def __init__(self):
        super().__init__()


class BadSchemaException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)
