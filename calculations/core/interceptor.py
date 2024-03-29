import time
from functools import wraps

from calculations.core import LOG


def interceptor(func):
    """ Intercept each functioin """

    @wraps(func)
    def wrapper(*func_args, **func_kwargs):
        """ Log before and after the function """

        """ Extract function arguments """
        # arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        # args = func_args[:len(arg_names)]
        # defaults = func.__defaults__ or ()
        # args = args + defaults[len(defaults) - (func.__code__.co_argcount - len(args)):]
        # params = list(zip(arg_names, args))
        # args = func_args[len(arg_names):]
        # if args:
        #     params.append(('args', args))
        # if func_kwargs:
        #     params.append(('kwargs', func_kwargs))

        """ Log start -> Excute function -> Log end """
        start_time = time.time()
        # LOG.info(f"====== Start {func.__qualname__} {'( ' + ', '.join('%s = %r' % p for p in params) + ' )'}======")
        LOG.info(f"====== Start {func.__qualname__} ======")
        result = func(*func_args, **func_kwargs)
        LOG.info(f"====== End {func.__qualname__} ====== " + "{:.4f}s".format(time.time() - start_time))
        return result

    return wrapper

# def interceptor_log(variable):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             # set name_override to func.__name__
#             # log.info("Gen log", extra={'name_override': func.__name__})
#             LOG.info(f"====== Start {func.__name__} ======")
#             result = func(*args, **kwargs)
#             LOG.info(f"====== End {func.__name__} ======")
#             return result
#
#         return wrapper
#
#     return decorator
