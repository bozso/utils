import os
import os.path as path
import glob
import subprocess as sub
import shutil as sh

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
        return Path(path.join(self._path, *args))
    
    def iglob(self, *args, **kwargs):
        for elem in glob.iglob(self._path, *args, **kwargs):
            yield Path(elem)
    
    def move(self, target):
        try:
            return Path(sh.move(self._path, target))
        except sh.Error:
            os.unlink(self._path)
            return Path(target)
    
    def replace_ext(self, new_ext):
        s = self._path.split(".")
        
        return Path.joined("%s.%s" % (".".join(s[:-1]), new_ext))
    
    def glob(self):
        return tuple(self.iglob())
    
    def exists(self):
        return path.exists(self._path)
    
    def isfile(self):
        return path.isfile(self._path)
    
    def basename(self):
        return Path(path.basename(self._path))
    
    def __str__(self):
        return self._path
        
    def __fspath__(self):
        return self._path
    
