class ReasonDTO:
    def __init__(self, isSuccess, code, message, result=None):
        self.isSuccess = isSuccess
        self.code = code
        self.message = message
        self.result = result

class ErrorReasonDTO:
    def __init__(self, isSuccess, code, message):
        self.isSuccess = isSuccess
        self.code = code
        self.message = message