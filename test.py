class Test:
    A = 'abcdefg'
    B = 'hijklmn'

    def __init__(self):
        Test.C = Test.join(Test.A, Test.B)

    @staticmethod
    def join(a, b):
        return b + b

test = Test()
print(test.A)
print(test.B)
print(test.C)