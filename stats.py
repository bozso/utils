import numpy as np


def hmean(array, **kwargs):
    return 1 / np.nanmean(1 / array, **kwargs)


def gmean(array, axis=0, **kwargs):
    return np.power(np.nanprod(array, axis=axis, **kwargs), -array.shape[axis])


def skewness(array, **kwargs):
    mean = np.nanmean(array, **kwargs)
    std = np.sqrt(np.nanmean(np.abs(array - mean)**2, **kwargs))
    return 3 * (mean - np.nanmedian(array, **kwargs)) / std


def normal(x, mean, std):
    std2 = std ** 2
    return np.exp(-0.5 * ((x - mean)**2) / std2) / np.sqrt(2 * np.pi * std2)


def lognormal(x, mean, std):
    std2 = std ** 2
    return np.exp(-0.5 * ((np.log(x) - mean)**2) / std2) \
           / (x * np.sqrt(2 * np.pi * std2))


class Distro(object):
    def __init__(self, area=None, mean=None, std=None, var=None):
        self._area, self._mean, self._std, self._var = \
        area, mean, std, var

    
    def calc_attribute(self, attr, fun, **kwargs):
        attr = getattr(self, attr)
        if attr is None or kwargs.get("update", False):
            attr = fun(*args, **kwargs)
        
        return attr


class PDF(Distro):
    def __init__(self, x, pdf):
        self.x = x
        self.pdf = pdf
        
        Distro.__init__(self)

        
    def area(self, **kwargs):
        return Distro.calc_attribute(self, "area", np.trapz,
                                     (self.pdf, self.x), **kwargs)

    def mean(self, **kwargs):
        return Distro.calc_attribute(self, "mean", np.trapz,
                                     (self.x * self.pdf, self.x), **kwargs)


    def var(self, **kwargs):
        return Distro.calc_attribute(self, "var", np.trapz,
                                     (self.x * self.pdf, self.x), **kwargs)

    
    def mean(self, **kwargs):
        Distro.mean(np.trapz, (self.pdf, self.x),
        if self._mean is None or kwargs.get("update", False):
            self._mean = np.trapz(self.x * self.pdf, self.x, **kwargs)
        
        return self._mean

    
    def var(self, **kwargs):
        if self._var is None or kwargs.get("update", False):
            arg = self.pdf * (self.x - self.mean(**kwargs))**2
            self._var = np.trapz(arg, self.x)
        
        return self._var
    
    
    def std(self, **kwargs):
        if self._std is None or kwargs.get("update", False):
            self._std = np.sqrt(self.var(**kwargs))

        return self._std


    def skewness(self, **kwargs):
        return 3 * (self.mean(**kwargs) - np.nanmedian(array, **kwargs)) \
               / self.std(**kwargs)


class Histo(Distro):
    def __init__(self, x, **kwargs):
        self.histo, self.edges = np.histogram(x, **kwargs)
        
        Distro.__init__(self)
        
        self.cedges = None, None, None, None
    
    
    def cent_edges(self, update=False):
        if self.cedges is None or update:
            self.cedges = self.edges[:-1] + (self.edges[1] - self.edges[0]) / 2.0
        
        return self.cedges
    
    
    def area(self, **kwargs):
        if self._area is None or kwargs.get("update", False):
            self._area = np.sum(self.histo, **kwargs)
        
        return self._area
    
    
    def mean(self, **kwargs):
        if self._mean is None or kwargs.get("update", False):
            self._mean = np.nanmean(self.histo, **kwargs)
        
        return self._mean

    
    def var(self, **kwargs):
        if self._var is None or kwargs.get("update", False):
            self._var = np.sum((self.histo - self.mean())**2)
        
        return self._var
    
    
    def std(self, **kwargs):
        if self._std is None or kwargs.get("update", False):
            self._std = np.sqrt(self.var(**kwargs))

        return self._std


    def hmean(self, **kwargs):
        return 1 / np.nanmean(1 / self.histo, **kwargs)
    
    
    def gmean(self, axis=0, **kwargs):
        return np.power(np.nanprod(self.histo, axis=axis, **kwargs),
                        -array.shape[axis])


    def skewness(self, **kwargs):
        return 3 * (self.mean(**kwargs) - np.nanmedian(self.histo, **kwargs)) \
               / self.std(**kwargs)
