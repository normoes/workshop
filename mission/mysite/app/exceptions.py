

class RpcConnectionError(Exception):
    """Exception in combination with wallet RPCs.
    """

    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors
