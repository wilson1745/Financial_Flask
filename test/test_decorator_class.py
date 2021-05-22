import types


class ClassDecorator:
    """ 類別裝飾器 """

    def __init__(self, func):
        self.numberOfCalls = 0
        self.func = func

    # __call__是定義當該方法被呼叫到時的處置方式
    def __call__(self, *args, **kwargs):
        self.numberOfCalls += 1
        return self.func(*args, **kwargs)

    # __get__方法是为了確保綁定方法對象能被正確的創建
    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)


# 使用於方法上則__get__可有可無
@ClassDecorator
def add(x, y):
    return x + y


class Decorated:
    @ClassDecorator
    def bar(self, x):
        print(self, x)


print(add(2, 3))
print(add(4, 5))
print(add.numberOfCalls)

s = Decorated()
s.bar(1)
s.bar(2)
s.bar(3)

s2 = Decorated()
s2.bar(1)
s2.bar(2)
s2.bar(3)
print(Decorated.bar.numberOfCalls)
