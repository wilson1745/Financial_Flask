import logging
from functools import wraps

log = logging.getLogger("projects")


def interceptor(func):
    """ Intercept each functioin """

    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        # Extract function arguments
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        args = func_args[:len(arg_names)]
        defaults = func.__defaults__ or ()
        args = args + defaults[len(defaults) - (func.__code__.co_argcount - len(args)):]
        params = list(zip(arg_names, args))
        args = func_args[len(arg_names):]
        if args:
            params.append(('args', args))
        if func_kwargs:
            params.append(('kwargs', func_kwargs))

        # Log before and after the function
        log.info(f"====== Start {func.__name__} {'(' + ', '.join('%s = %r' % p for p in params) + ' )'}======")
        result = func(*func_args, **func_kwargs)
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
