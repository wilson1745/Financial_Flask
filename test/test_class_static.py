class ObjectA:
    def func(self, *args, **kwargs):
        print("executing func(%s)" % self)

    @classmethod
    def func_class(cls, *args, **kwargs):
        print("executing class_foo(%s)" % cls)

    @staticmethod
    def func_static(*args, **kwargs):
        print("executing static_foo()")


# var = ObjectA()
# var.func()

ob1 = ObjectA()
ob2 = ObjectA()

ob1.func()
ob2.func()

ob1.func_class()
ob2.func_class()

print(ob1.func_static)
print(ob2.func_static)
print(ObjectA.func_static)
