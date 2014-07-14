

class ValidationFailed(ValueError):
    """User input was inconsistent with API restrictions"""

    def __init__(self, msg, *args, **kwargs):
        msg = msg.format(*args, **kwargs)
        super(ValidationFailed, self).__init__(msg)


class ValidationProgrammingError(ValueError):
    """Caller did not map validations correctly"""

    def __init__(self, msg, *args, **kwargs):
        msg = msg.format(*args, **kwargs)
        super(ValidationProgrammingError, self).__init__(msg)
