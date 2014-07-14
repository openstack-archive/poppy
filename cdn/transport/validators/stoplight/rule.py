
from collections import namedtuple

ValidationRule = namedtuple('ValidationRule', 'vfunc errfunc getter')


def Rule(vfunc, on_error, getter=None):
    """Constructs a single validation rule. A rule effectively
    is saying "I want to validation this input using
    this function and if validation fails I want this (on_error)
    to happen.

    :param vfunc: The function used to validate this param
    :param on_error: The function to call when an error is detected
    :param value_src: The source from which the value can be
        This function should take a value as a field name
        as a single param.
    """
    return ValidationRule(vfunc=vfunc, errfunc=on_error, getter=getter)
