from functools import wraps

from calculations import log


def interceptor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log.info(f"====== Start {func.__name__} ======")
        result = func(*args, **kwargs)
        log.info(f"====== End {func.__name__} ======")
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


# def getLogger():
#     # TODO check if LOG has not initialized!!!
#     # LOG.debug(f"id(log): {hex(id(LOG))}")
#     return log
