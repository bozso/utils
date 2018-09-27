
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

    def __truediv__(self, other):
        return RPN._op("DIV", self, other)

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

    def __neg__(self):
        return RPN._op("NEG", self)
    

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


def acos(A):
    return RPN._op("ACOS", A)

def acosh(A):
    return RPN._op("ACOSH", A)

def acsc(A):
    return RPN._op("ACSC", A)

def acot(A):
    return RPN._op("ACOT", A)

def AND(A, B):
    return RPN._op("AND", A, B)

def asec(A):
    return RPN._op("ASEC", A)

def asin(A):
    return RPN._op("ASIN", A)

def asinh(A):
    return RPN._op("ASINH", A)

def atan(A, B=None):
    if B is None:
        return RPN._op("ATAN", A)
    else:
        return RPN._op("ATAN2", A, B)

def atanh(A):
    return RPN._op("ATANH", A)

def bcdf(A, B, C):
    """Binomial cumulative distribution function for p = A, n = B, and x = C"""
    return RPN._op("BCDF", A, B, C)

def bpdf(A, B, C):
    """Binomial probability density function for p = A, n = B, and x = C"""
    return RPN._op("BPDF", A, B, C)

def bei(A):
    return RPN._op("BEI", A)

def ber(A):
    return RPN._op("BER", A)

def bittest(A, B):
    """1 if bit B of A is set, else 0 (bitwise TEST operator) """
    return RPN._op("BITTEST", A, B)

def chicrit(A, B):
    """Chi-squared distribution critical value for alpha = A and nu = B"""
    return RPN._op("CHICRIT", A, B)

def chicdf(A, B):
    """Chi-squared cumulative distribution function for chi2 = A and nu = B"""
    return RPN._op("CHICCDF", A, B)

def chipdf(A, B):
    """Chi-squared probability density function for chi2 = A and nu = B"""
    return RPN._op("CHICPDF", A, B)

def col(A):
    """Places column A on the stack"""
    return RPN._op("COL", A)

def comb(A, B):
    """Combinations n_C_r, with n = A and r = B"""
    return RPN._op("COMB", A, B)

def corr(A, B):
    """Correlation coefficient r(A, B)"""
    return RPN._op("CORRCOEFF", A, B)

def cos(A):
    """cos (A) (A in radians)"""
    return RPN._op("COS", A)

def cosd(A):
    """cosd (A) (A in degrees)"""
    return RPN._op("COSD", A)

def cosh(A):
    """cosh (A)"""
    return RPN._op("COSH", A)

def cot(A):
    """cot (A) (A in radians)"""
    return RPN._op("COT", A)

def cotd(A):
    """cotd (A) (A in degrees)"""
    return RPN._op("COTD", A)

def csc(A):
    """csc (A) (A in radians)"""
    return RPN._op("CSC", A)

def cscd(A):
    """cscd (A) (A in degrees)"""
    return RPN._op("CSCD", A)

def ddt(A):
    """d(A)/dt Central 1st derivative"""
    return RPN._op("DDT", A)

def d2dt2(A):
    """d^2(A)/dt^2 2nd derivative"""
    return RPN._op("D2DT2", A)

def d2r(A):
    """Converts Degrees to Radians"""
    return RPN._op("D2R", A)

def denan(A, B):
    """Replace NaNs in A with values from B"""
    return RPN._op("DENAN", A, B)

def dilog(A):
    """dilog (A)"""
    return RPN._op("DILOG", A)

def diff(A):
    """Difference between adjacent elements of A (A[1]-A[0], A[2]-A[1], ..., 0)"""
    return RPN._op("DIFF", A)

def dup(A):
    """Places duplicate of A on the stack"""
    return RPN._op("DUP", A)

def ecdf(A, B):
    """Exponential cumulative distribution function for x = A and lambda = B"""
    return RPN._op("ECDF", A, B)

def ecrit(A, B):
    """Exponential distribution critical value for alpha = A and lambda = B"""
    return RPN._op("ECRIT", A, B)

def epdf(A, B):
    """Exponential probability density function for x = A and lambda = B"""
    return RPN._op("EPDF", A, B)

def erf(A):
    """Error function erf (A)"""
    return RPN._op("ERF", A)

def erfc(A):
    """Complementary Error function erf (A)"""
    return RPN._op("ERFC", A)

def erfinv(A):
    """Inverse Error function erf (A)"""
    return RPN._op("ERFINV", A)

def exch(A, B):
    """Exchanges A and B on the stack"""
    return RPN._op("EXCH", A, B)

def exp(A):
    """exp (A)"""
    return RPN._op("EXP", A)

def fact(A):
    """A! (A factorial)"""
    return RPN._op("FACT", A)

def fcdf(A, B, C):
    """F cumulative distribution function for F = A, nu1 = B, and nu2 = C"""
    return RPN._op("FCDF", A, B, C)

def fcrit(A, B, C):
    """F distribution critical value for alpha = A, nu1 = B, and nu2 = C"""
    return RPN._op("FCRIT", A, B, C)

def flipud(A):
    """Reverse order of each column"""
    return RPN._op("FLIPUD", A)

def fpdf(A):
    """F probability density function for F = A, nu1 = B, and nu2 = C"""
    return RPN._op("FPDF", A, B, C)

def hypot(A, B):
    """hypot (A, B) = sqrt (A*A + B*B)"""
    return RPN._op("HYPOT", A, B)

def I0(A):
    """Modified Bessel function of A (1st kind, order 0)"""
    return RPN._op("I0", A)

def I1(A):
    """Modified Bessel function of A (1st kind, order 1)"""
    return RPN._op("I1", A)

def IN(A, B):
    """Modified Bessel function of A (1st kind, order B)"""
    return RPN._op("IN", A, B)

def ifelse(A, B, C):
    """B if A != 0, else C"""
    return RPN._op("IFELSE", A, B, C)

def inrange(A, B, C):
    """1 if B <= A <= C, else 0"""
    return RPN._op("INRANGE", A, B, C)

def INT(A):
    """Numerically integrate A"""
    return RPN._op("INT", A)

def inv(A):
    """1 / A"""
    return RPN._op("INV", A)

def isfinite(A):
    """1 if A is finite, else 0"""
    return RPN._op("ISFINITE", A)

def isnan(A):
    """1 if A == NaN, else 0"""
    return RPN._op("ISNAN", A)

def J0(A):
    """Bessel function of A (1st kind, order 0)"""
    return RPN._op("J0", A)

def J1(A):
    """Bessel function of A (1st kind, order 1)"""
    return RPN._op("J1", A)

def JN(A, B):
    """Bessel function of A (1st kind, order B)"""
    return RPN._op("JN", A, B)

def K0(A):
    """Modified Kelvin function of A (2nd kind, order 0)"""
    return RPN._op("K0", A)

def K1(A):
    """Modified Kelvin function of A (2nd kind, order 1)"""
    return RPN._op("K1", A)

def KN(A, B):
    """Modified Kelvin function of A (2nd kind, order B)"""
    return RPN._op("KN", A, B)

def kei(A):
    """kei (A)"""
    return RPN._op("KEI", A)

def ker(A):
    """ker (A)"""
    return RPN._op("KER", A)

def kurt(A):
    """Kurtosis of A"""
    return RPN._op("KURT", A)

def lcdf(A):
    """Laplace cumulative distribution function for z = A"""
    return RPN._op("LCDF", A)

def lcrit(A):
    """Laplace distribution critical value for alpha = A"""
    return RPN._op("LCRIT", A)

def lmsscl(A):
    """LMS scale estimate (LMS STD) of A"""
    return RPN._op("LMSSCL", A)

def log(A):
    """log (A) (natural log)"""
    return RPN._op("LOG", A)

def log10(A):
    """log10 (A) (base 10)"""
    return RPN._op("LOG10", A)

def log10p(A):
    """log (1+A) (accurate for small A)"""
    return RPN._op("LOG10P", A)

def log2(A):
    """log2 (A) (base 2)"""
    return RPN._op("LOG2", A)

def lower(A):
    """The lowest (minimum) value of A"""
    return RPN._op("LOWER", A)

def lower(A):
    """The lowest (minimum) value of A"""
    return RPN._op("LOWER", A)

def lpdf(A):
    """Laplace probability density function for z = A"""
    return RPN._op("LPDF", A)

def lrand(A):
    """Laplace random noise with mean A and std. deviation B"""
    return RPN._op("LRAND", A)

def lsqfit(A):
    """Let current table be [A | b] return least squares solution x = A \ b"""
    return RPN._op("LSQFIT", A)

def mad(A):
    """Median Absolute Deviation (L1 STD) of A"""
    return RPN._op("MAD", A)

def max(A, B):
    """Maximum of A and B"""
    return RPN._op("MAX", A, B)

def mean(A):
    """Mean value of A"""
    return RPN._op("MEAB", A)

def med(A):
    """Median value of A"""
    return RPN._op("MED", A)

def min(A):
    """Minimum of A and B"""
    return RPN._op("MIN", A)

def mode(A):
    """Mode value (Least Median of Squares) of A"""
    return RPN._op("MODE", A)

def nan(A, B):
    """NaN if A == B, else A"""
    return RPN._op("NAN", A, B)

def norm(A):
    """Normalize (A) so max(A)-min(A) = 1"""
    return RPN._op("NORM", A)

def NOT(A):
    """NaN if A == NaN, 1 if A == 0, else 0"""
    return RPN._op("NOT", A)

def nrand(A, B):
    """Normal, random values with mean A and std. deviation B"""
    return RPN._op("NRAND", A, B)

def OR(A, B):
    """NaN if B == NaN, else A"""
    return RPN._op("OR", A, B)

def pcdf(A, B):
    """Poisson cumulative distribution function for x = A and lambda = B"""
    return RPN._op("PCDF", A, B)

def ppdf(A, B):
    """Poisson distribution P(x,lambda), with x = A and lambda = B"""
    return RPN._op("PPDF", A, B)

def perm(A, B):
    """Permutations n_P_r, with n = A and r = B"""
    return RPN._op("PERM", A, B)

def plm(A, B, C):
    """Associated Legendre polynomial P(A) degree B order C"""
    return RPN._op("PLM", A, B, C)

def plmg(A, B, C):
    """
    Normalized associated Legendre polynomial P(A) degree B order
    C (geophysical convention)
    """
    return RPN._op("PLMg", A, B, C)

def pop():
    """Delete top element from the stack"""
    return RPN._op("POP")

def pow(A, B):
    """A ^ B"""
    return RPN._op("POW", A, B)

def pquant(A, B):
    """The B’th Quantile (0-100%) of A"""
    return RPN._op("PQUANT", A, B)

def psi(A):
    """Psi (or Digamma) of A"""
    return RPN._op("PSI", A, B)

def pv(A, B, C):
    """Legendre function Pv(A) of degree v = real(B) + imag(C)"""
    return RPN._op("PV", A, B, C)

def qv(A, B, C):
    """Legendre function Qv(A) of degree v = real(B) + imag(C)"""
    return RPN._op("QV", A, B, C)

def R2(A, B):
    """R2 = A^2 + B^2"""
    return RPN._op("R2", A, B)

def r2d(A):
    """Convert Radians to Degrees"""
    return RPN._op("R2D", A)

def rand(A, B):
    """Uniform random values between A and B"""
    return RPN._op("RAND", A, B)

def rcdf(A):
    """Rayleigh cumulative distribution function for z = A"""
    return RPN._op("RCDF", A)

def rcrit(A):
    """Rayleigh distribution critical value for alpha = A"""
    return RPN._op("RCRIT", A)

def rpdf(A):
    """Rayleigh probability density function for z = A"""
    return RPN._op("RPDF", A)

def roll(A, B):
    """Cyclicly shifts the top A stack items by an amount B"""
    return RPN._op("ROLL", A, B)

def rott(A, B):
    """Rotate A by the (constant) shift B in the t-direction"""
    return RPN._op("ROTT", A, B)

def sec(A):
    """sec (A) (A in radians)"""
    return RPN._op("SEC", A)

def secd(A):
    """secd (A) (A in degrees)"""
    return RPN._op("SECD", A)

def sign(A):
    """sign (+1 or -1) of A"""
    return RPN._op("SIGN", A)

def sin(A):
    """sin (A) (A in radians)"""
    return RPN._op("SIN", A)

def sinc(A):
    """sinc (A) (sin (pi*A)/(pi*A))"""
    return RPN._op("SINC", A)

def sinc(A):
    """sinc (A) (sin (pi*A)/(pi*A))"""
    return RPN._op("SINC", A)

def sind(A):
    """sind (A) (A in degrees)"""
    return RPN._op("SIND", A)

def sinh(A):
    """sinh (A)"""
    return RPN._op("SINH", A)

def skew(A):
    """Skewness of A"""
    return RPN._op("SKEW", A)

def sqr(A):
    """A^2"""
    return RPN._op("SQR", A)

def sqrt(A):
    """sqrt (A)"""
    return RPN._op("SQRT", A)

def std(A):
    """Standard deviation of A"""
    return RPN._op("STD", A)

def step(A):
    """Heaviside step function H(A)"""
    return RPN._op("STEP", A)

def stept(A):
    """Heaviside step function H(t - A)"""
    return RPN._op("STEPT", A)

def csum(A):
    """Cumulative sum of A"""
    return RPN._op("SUM", A)

def tanh(A):
    """tanh (A)"""
    return RPN._op("TANH", A)



def spec(a, b, c):
    return a + b * acos(c)

if __name__ == "__main__":
    data1 = GRD("data1.grd")
    data2 = GRD("data2.grd")
    
    print(spec(data2, data1, data2))
    
    
