import logging
from functools import wraps

log = logging.getLogger("projects")


def interceptor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log.info(f"====== Start {func.__name__} ======")
        result = func(*args, **kwargs)
        log.info(f"====== End {func.__name__} ======")
        return result

    return wrapper


class ClassTest:
    name = ''

    def __init__(self, name):
        self.name = name

    @classmethod
    def printArgs(cls, arg):
        def decorator(func):
            @wraps(func)
            def warpper(*args, **kwargs):
                print(func.__name__)
                print(func.__doc__)
                print(arg)
                return func(*args, **kwargs)

            return warpper

        return decorator
