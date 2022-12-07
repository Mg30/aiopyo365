class GraphApiError(Exception):
    """Encapsulate error from Microsoft Graph API

    ref: https://docs.microsoft.com/en-us/graph/errors
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return str(self.message)
