import glob
import os.path as path

from utils import Ninja

class ProjectMixin(object):
    def push(self):
        pass
        
    def commit(self):
        pass

class Git(object):
    pass

class Project(object):
    __slots__ = (
        "root",
    )
    
    def __init__(self, filepath):
        self.root = path.dirname(path.abspath(filepath))


class SourceLister(object):
    def list_sources(self, *args):
        return glob.glob(path.join(*args, self.extension))
    
    def gather_sources(self):
        ext = "*.%s" % self.extension
        
        return sum(
            (
                self.list_sources(sdir, ext)
                for sdir in self.subdirs
            ),
            []
        )
        

class Go(ProjectMixin, SourceLister):
    __slots__ = (
        "project", "subdirs", "name",
    )
    
    release_flags = "-ldflags '-s -w' -trimpath ."
    extension = "go"
    
    def __init__(self, *args, **kwargs):
        self.project, self.subdirs, self.name = (
            Project(*args, **kwargs),
            kwargs.get("subdirs", set()),
            kwargs["name"]
        )
    
    def generate_ninja(self):
        root, name = self.root, self.name
        
        main = path.join(root, name)
        
        cmd = "go build %s -o ${out} ${in}"
        
        ninja = path.join(root, "build.ninja")
        
        n = ut.Ninja.in_path(root)
        n.rule("go", cmd % "", "Build debug executable.")
        
        n.rule("go-release", cmd % self.release_flags,
            "Build release executable.")
        
        n.newline()
        
        src = self.gather_sources()
        
        n.build(main, "go", main + ".go", implicit=src)
        n.build(main, "go-release", main + ".go", implicit=src)
        n.newline()
        
        for sdir in self.subdirs:
            n = ut.Ninja.in_path(sdir)
            n.subninja(ninja)
    
