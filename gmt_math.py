
class RPN(object):
    
    @staticmethod
    def _op(op, *args):
        return MathExp("{} {}".format(" ".join(str(arg) for arg in args), op))

    def __add__(self, other):
        return RPN._op("ADD", self, other)

    def __sub__(self, other):
        return RPN._op("SUB", self, other)

    def __mul__(self, other):
        return RPN._op("MUL", self, other)

    def __mod__(self, other):
        return RPN._op("MOD", self, other)

    def __lt__(self, other):
        return RPN._op("LT", self, other)

    def __le__(self, other):
        return RPN._op("LE", self, other)

    def __eq__(self, other):
        return RPN._op("EQ", self, other)

    def __ne__(self, other):
        return RPN._op("NEQ", self, other)

    def __gt__(self, other):
        return RPN._op("GT", self, other)

    def __ge__(self, other):
        return RPN._op("GE", self, other)

    def __lshift__(self, other):
        return RPN._op("BITLEFT", self, other)

    def __rshift__(self, other):
        return RPN._op("BITRIGHT", self, other)

    def __and__(self, other):
        return RPN._op("BITAND", self, other)

    def __or__(self, other):
        return RPN._op("BITOR", self, other)

    def __xor__(self, other):
        return RPN._op("BITXOR", self, other)

    def __invert__(self, other):
        return RPN._op("BITNOT", self, other)

    def __abs__(self):
        return RPN._op("ABS", self)

    def __round__(self):
        return RPN._op("RINT", self)

    def __floor__(self):
        return RPN._op("FLOOR", self)

    def __ceil__(self):
        return RPN._op("CEIL", self)
    

class GRD(RPN):
    def __init__(self, grdfile):
        self.grdfile = str(grdfile)
    
    def __str__(self):
        return self.grdfile

    
class MathExp(RPN):
    def __init__(self, string):
        self.string = str(string)
    
    def __str__(self):
        return self.string


def acos(data):
    return RPN._op("ACOS", data)

def acosh(data):
    return RPN._op("ACOSH", data)

def acsc(data):
    return RPN._op("ACSC", data)

def acot(data):
    return RPN._op("ACOT", data)

def AND(one, two):
    return RPN._op("AND", one, two)

def asec(data):
    return RPN._op("ASEC", data)

def asin(data):
    return RPN._op("ASIN", data)

def asinh(data):
    return RPN._op("ASINH", data)

def atan(one, two=None):
    if two is None:
        return RPN._op("ATAN", one)
    else:
        return RPN._op("ATAN2", one, two)

def atanh(data):
    return RPN._op("ATANH", data)

def bcdf(one, two, three):
    return RPN._op("BCDF", one, two, three)





if __name__ == "__main__":
    data1 = GRD("data1.grd")
    data2 = GRD("data2.grd")
    
    print(abs(data1 + data2 - data1) + acos(data1))
    
    
