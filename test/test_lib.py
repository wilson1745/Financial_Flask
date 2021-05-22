from projects.common.interceptor import ClassTest

if __name__ == '__main__':
    # cls = ClassA('ClassName')
    # cls.printName()

    @ClassTest.printArgs('Hello')
    def printArgs(args):
        """ DOC """
        print(args)


    printArgs('World')
    print(printArgs.__name__)
    print(printArgs.__doc__)
