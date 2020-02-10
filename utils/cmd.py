import subprocess as sub
import shlex

__all__ = (
    "Command", "subcommands",
)

class Parser(object):
    __slots__ = ("template", "bool_template")
    
    def __init__(self, **kwargs):
        kwargs.setdefault("separator", "=")
        kwargs.setdefault("prefix", "--")
        
        self.template = "{prefix}%s{separator}%s".format(**kwargs)
        self.bool_template = "{prefix}%s".format(**kwargs)
    
    def parse(self, key, val):
        if val is True:
            return self.bool_template % (key)
        
        return self.template % (key, val)


class Command(object):
    __slots__ = ("cmd", "parser")
    
    error_tpl = ("\nNon zero returncode from command: \n'{}'\n"
                 "\nOUTPUT OF THE COMMAND: \n\n{}\nRETURNCODE was: {}")

    def __init__(self, cmd, parser):
        self.cmd, self.parser = cmd, parser
    
    @classmethod
    def with_parser(cls, cmd, **kwargs):
        return cls(cmd, Parser(**kwargs))
    
    def __call__(self, *args, **kwargs):
        p = self.parser
        debug = kwargs.pop("_debug_", False)
        
        Cmd = self.cmd
        
        if len(args) > 0:
            Cmd += " %s" % " ".join(args)
        
        if len(kwargs) > 0:
            Cmd += " %s" % " ".join(
                p.parse(key, val) for key, val in kwargs.items()
            )
        
        if debug:
            print("Command is '%s'" % Cmd)
            return
        
        try:
            proc = sub.check_output(shlex.split(Cmd), stderr=sub.STDOUT)
        except sub.CalledProcessError as e:
            raise RuntimeError(
                self.error_tpl.format(Cmd, e.output.decode(),
                    e.returncode)
            )
    
        return proc


def subcommands(root, *args, **kwargs):
    p = Parser(**kwargs)
    
    return type(root, (object,),
        {
            cmd: Command.with_parser("%s %s" % (root, cmd), p) 
            for cmd in args
        }
    )
