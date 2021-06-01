def printHello(func):
    def wrapper(*args, **kwargs):
        print("\nHello")
        return func(*args, **kwargs)

    return wrapper


def printArg(arg):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(arg)
            return func(*args, **kwargs)

        return wrapper

    return decorator


@printHello
def printWorld():
    print("World")


# @printHello
# def printArg(arg):
#     print(arg)


def funcs(*args, **kwargs):
    """ *args與**kwargs """
    for item in args:
        print("I'm args and value is {0}".format(item))
    for key, value in kwargs.items():
        print("I'm kwargs and key and value is {0}={1}".format(key, value))


@printArg("Hi")
def sayHiAndPrintArg(param):
    """ 裝飾器也能加參數 """
    print(param)


# printWorld()
#
# printArg("FFFFF")
# printArg("Kitty")

# funcs([{
#     'name': 10,
#     'value': 20
# }, 1, 2, 3], 12364)
#
# funcs(name=1023)

sayHiAndPrintArg("World")

