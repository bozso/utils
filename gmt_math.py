
class DataFile(object):
    def __init__(self):
        pass
    
    def _op(self):
        pass

    def __add__(self, other):
        _op(self, other, "+")

    def __sub__(self, other):
        _op(self, other, "+")

    def __mul__(self, other):
        _op(self, other, "+")

    def __mod__(self, other):
        _op(self, other, "+")

    def __lt__(self, other):
        _op(self, other, "+")

    def __le__(self, other):
        _op(self, other, "+")

    def __eq__(self, other):
        _op(self, other, "+")

    def __ne__(self, other):
        _op(self, other, "+")

    def __gt__(self, other):
        _op(self, other, "+")

    def __ge__(self, other):
        _op(self, other, "+")

    def __lshift__(self, other):
        _op(self, other, "+")

    def __rshift__(self, other):
        _op(self, other, "+")

    def __and__(self, other):
        _op(self, other, "+")

    def __or__(self, other):
        _op(self, other, "+")

    def __xor__(self, other):
        _op(self, other, "+")

    def __invert__(self, other):
        _op(self, other, "+")


class MathExp(object):
    def __init__(self, string):
        self.string = str(string)
    
    def _op(self, other):
        pass

    def __add__(self, other):
        _op(self, other, "+")

    def __sub__(self, other):
        _op(self, other, "+")

    def __mul__(self, other):
        _op(self, other, "+")

    def __mod__(self, other):
        _op(self, other, "+")

    def __lt__(self, other):
        _op(self, other, "+")

    def __le__(self, other):
        _op(self, other, "+")

    def __eq__(self, other):
        _op(self, other, "+")

    def __ne__(self, other):
        _op(self, other, "+")

    def __gt__(self, other):
        _op(self, other, "+")

    def __ge__(self, other):
        _op(self, other, "+")

    def __lshift__(self, other):
        _op(self, other, "+")

    def __rshift__(self, other):
        _op(self, other, "+")

    def __and__(self, other):
        _op(self, other, "+")

    def __or__(self, other):
        _op(self, other, "+")

    def __xor__(self, other):
        _op(self, other, "+")

    def __invert__(self, other):
        _op(self, other, "+")

    
    def __str__(self):
        return self.string

def _op(op, *args):
    return ("{} {}".format(" ".join(str(arg) for arg in args), op))

if __name__ == "__main__":
    print(_op("+", "a.grd", "b.grd"))
