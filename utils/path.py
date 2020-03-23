import os
import os.path as path
import glob
import subprocess as sub
import shutil as sh
import functools as ft

from shlex import split

__all__ = (
    "cd", "Path",
)

class cd(object):
    """Context manager for changing the current working directory"""
    
    __slots__ = (
        "newPath", "savedPath",
    )
    
    def __init__(self, p):
        self.newPath, self.savedPath = (
            path.expanduser(p),
            None
        )

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)    

    @classmethod
    def call(cls, cmd, *args, **kwargs):
        with cls(*args, **kwargs):
            sub.call(split(cmd))        


class Path(object):
    json_serialize = (
        "_path",
    )
    
    __slots__ = json_serialize
    
    def __init__(self, path):
        self._path = path
    
    def get_path(self):
        return self._path
    
    @classmethod
    def expanduser(cls, p):
        return cls(path.expanduser(p))

    @classmethod
    def joined(cls, *args):
        return cls(path.join(*args))
    
    @classmethod
    def cwd(cls):
        return cls(os.getcwd())
    
    def mkdir(self):
        p = self._path
        
        if not self.exists():
            os.makedirs(p)
            
        return Path(p)
    
    def join(self, *args):
        p = path.join(*tuple(map(str, args)))
        
        return Path(path.join(self._path, p))
    
    def iglob(self, *args, **kwargs):
        for elem in glob.iglob(self._path, *args, **kwargs):
            yield Path(elem)

    def glob(self):
        return tuple(self.iglob())

    def move(self, target):
        try:
            return Path(sh.move(self._path, target))
        except sh.Error:
            os.unlink(self._path)
            return Path(target)
    
    def add_ext(self, ext):
        return Path("%s.%s" % (self._path, ext))
    
    def replace_ext(self, new_ext):
        s = self._path.split(".")
        
        return Path.joined("%s.%s" % (".".join(s[:-1]), new_ext))
        
    def exists(self):
        return path.exists(self._path)
    
    def isfile(self):
        return path.isfile(self._path)
        
    def __str__(self):
        return self._path
        
    def __fspath__(self):
        return self._path    

def applier(fn):
    @ft.wraps(fn)
    def inner(self, *args, **kwargs):
        return Path(fn(self._path, *args, **kwargs))
    
    return inner
    
Path.dirname = applier(path.dirname)
Path.basename = applier(path.basename)
Path.abspath = applier(path.abspath)
