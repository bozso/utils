import os
import os.path as path
import glob

__all__ = (
    "cd", "Path",
)

class cd(object):
    """Context manager for changing the current working directory"""
    
    __slots__ = (
        "newPath", "savedPath",
    )
    
    def __init__(self, path):
        self.newPath, self.savedPath = (
            path.expanduser(path),
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
            sub.call(cmd)


class Path(object):
    __slots__ = ("path",)
    
    def __init__(self, path):
        self.path = path
    
    @classmethod
    def joined(cls, *args):
        return cls(path.join(*args))
    
    def mkdir(self):
        p = self.path
        
        if not self.exists():
            os.makedirs(p)
            
        return Path(p)
    
    def join(self, *args):
        return Path(path.join(self.path, *args))
    
    def iglob(self):
        return glob.iglob(self.path)

    def glob(self):
        return tuple(self.iglob())
    
    def exists(self):
        return path.exists(self.path)
    
    def isfile(self):
        return path.isfile(self.path)
    
    def __str__(self):
        return self.path
        
    def __fspath__(self):
        return self.path
