import functools as ft
import os
import operator as op
from itertools import tee, takewhile, islice, chain, filterfalse
from collections.abc import Iterable
from os import path as pth
from errno import EEXIST
from tempfile import _get_default_tempdir, _get_candidate_names
from shutil import copyfileobj
from shlex import split
from argparse import ArgumentParser
from glob import iglob
from sys import version_info
from keyword import iskeyword
from collections import OrderedDict
from copy import copy
from inspect import getfullargspec
from multiprocessing.pool import Pool
from subprocess import CalledProcessError, check_output, STDOUT

__all__ = (
    "Ninja", "HTML", "Seq", "flat", "new_type", "str_t", 
    "ls", "isiter", "all_same", "make_object", "tmp_file", "get_par", "cat", 
    "Files", "Multi", "Base", "CParse", "annot", "pos", "opt", "flag", "rm",
    "ln", "mv", "mkdir", "compose", "isfile", "fs", "Compiled", "C"
)

py3 = version_info[0] == 3

def flat(arg): return tup(chain.from_iterable(map(tup, arg)))

if py3:
    str_t = str,
else:
    str_t = basestring,


def make_cmd(command, tpl="--%s=%s"):
    def cmd(*args, **kwargs):
        debug = kwargs.pop("_debug_", False)
        
        Cmd = command
        
        if len(args) > 0:
            Cmd += " %s" % " ".join(args)
        
        if len(kwargs) > 0:
            Cmd += " %s" % " ".join(tpl % (key, val)
                                        for key, val in kwargs.items())
        
        if debug:
            print("Command is '%s'" % Cmd)
            return
        
        try:
            proc = check_output(split(Cmd), stderr=STDOUT)
        except CalledProcessError as e:
            raise RuntimeError("\nNon zero returncode from command: \n'{}'\n"
                "\nOUTPUT OF THE COMMAND: \n\n{}\nRETURNCODE was: {}"
                .format(Cmd, e.output.decode(), e.returncode))
        
        
        return proc
    return cmd

def cmd_line_prog(path, *args, **kwargs):
    prefix    = kwargs.pop("prefix", "--")
    separator = kwargs.pop("separator", "=")
    name = kwargs.pop("name", None)
    
    if name is None:
        name = path
    
    tpl = "%s%%s%s%%s" % (prefix, separator)
    
    cmds = {
        name: make_cmd("%s %s" % (path, name), tpl=tpl)
        for name in args
    }
    
    return make_object(name, cmds)


def fs(*elems):
    return frozenset(elems)

def compose2(f, g):
    return lambda *a, **kw: f(g(*a, **kw))
    
def compose(*functions):
    return ft.reduce(compose2, functions)


class TMP(object):
    tmpdir = _get_default_tempdir()
    
    def __init__(self):
        self.tmps = []
    
    def tmp_file(self, path=tmpdir):
        path = pth.join(path, next(_get_candidate_names()))
        
        self.tmps.append(path)
        
        return path
    
    def __del__(self):
        for path in self.tmps:
            rm(path)


tmp = TMP()
tmp_file = tmp.tmp_file

empty_iter = iter([])
isfile = compose(pth.isfile, pth.join)
ls = compose(iglob, pth.join)


    
def all_same(iterable, fun=None):
    if fun is not None:
        n = len(set(tee(map(fun, iterable),1)))
    else:
        n = len(set(tee(iterable,1)))
    
    return n == 1

def make_object(name, kwargs, inherit=(object,)):
    return type(name, inherit, kwargs)



def cat(out, *args):
    assert len(args) >= 1, "Minimum one input file is required"
    
    with open(out, 'wb') as f_out, open(args[0], 'rb') as f_in:
        copyfileobj(f_in, f_out)

    for arg in args[1:]:
        with open(out, 'ab') as f_out, open(arg, 'rb') as f_in:
            copyfileobj(f_in, f_out)


class Files(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def stat(self, attrib, rng=None, roff=0, loff=0, nr=None, nl=None):
        tmp = tmp_file()
        obj = getattr(self, attrib)
        
        if rng is None:
            rng = obj.rng()
        
        if isinstance(obj, string_t):
            gp.image_stat(obj, rng, roff, loff, nr, nl, tmp)
        else:
            gp.image_stat(obj.dat, rng, roff, loff, nr, nl, tmp)
        
        pars = Params.from_file(tmp)
        
        return pars
    

    def exist(self, *attribs):
        return all(pth.isfile(getattr(self, attrib)) for attrib in attribs)
    
    
    def mv(self, attrib, dst):
        Files._mv(getattr(self, attrib), dst)
    
    
    def move(self, attribs, dst):
        for attrib in attribs:
            attr = getattr(self, attrib)
            Files._mv(attr, dst)
            
            newpath = pth.join(pth.abspath(dst), pth.basename(attr))
            
            setattr(self, attrib, newpath)
    
    
    def rm(self, *attribs):
        for attrib in attribs:
            rm(getattr(self, attrib))
    
    def ln(self, attrib, other):
        ln(getattr(self, attrib), other)
    
    def cp(self, attrib, other):
        sh.copy(getattr(self, attrib), other)
    
    def set(self, attrib, key, **kwargs):
        return Files.set_par(key, getattr(self, attrib), **kwargs)
    
    
    def empty(self, attrib):
        return Files.is_empty(getattr(self, attrib))

    
    @staticmethod
    def _mv(src, dst):
        if pth.isfile(dst):
            dst_ = dst
        elif pth.isdir(dst):
            dst_ = pth.join(dst, pth.basename(src))
            
        rm(dst_)
        sh.move(src, dst_)
        
        log.debug('File "%s" moved to "%s".' % (src, dst_))


    @staticmethod
    def is_empty(path):
        return pth.getsize(path) == 0


def get_par(key, data, sep=":"):
    if pth.isfile(data):
        with open(data, "r") as f:
            lines = f.readlines()
    elif isinstance(data, bytes):
        lines = data.decode().split("\n")
    elif isinstance(data, str_t):
        lines = data.split("\n")
    else:
        lines = data
    
    for line in lines:
        if key in line:
            return " ".join(line.split(sep)[1:]).strip() 

    
def Multi(**kwargs):
    return type("Multi", (object,), kwargs)


class Base(Files):
    def __init__(self, base, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, "%s%s" % (base, value))
        
        self.base = base
    
    def rm(self):
        for elem in dir(self):
            Files.rm(self, elem)


def mkdir(path: str):
    try:
        os.makedirs(path)
        return path
    except OSError as e:
        if e.errno != EEXIST:
            raise e
        else:
            return path

mkdir = compose(mkdir, pth.join)


def ln(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e


def rm(*args):
    for arg in args:
        for path in iglob(arg):
            if not pth.isfile(path) and not pth.isdir(path):
                return
            elif pth.isdir(path):
                sh.rmtree(path)
            elif pth.isfile(path):
                try:
                    os.remove(path)
                except OSError as e:
                    if e.errno != ENOENT:
                        raise e
            else:
                raise Exception('"%s" is not a file nor is a directory!' % path)


def mv(*args, **kwargs):
    dst = kwargs.pop("dst", None)
    
    for arg in args:
        for src in iglob(arg): 
            rm(pth.join(dst, src))
            sh.move(src, dst)
            log.debug('"File "%s" moved to "%s".' % (src, dst))    

            
def pos(action="store", help=None, type=str, choices=None,
        nargs=None, metavar=None, dest=None, const=None):
    return {
        "action": action,
        "nargs": nargs,
        "type": type,
        "choices": choices,
        "help": help,
        "metavar": metavar,
        "kind": "pos"
        # "dest": dest,
    }


def opt(short=None, action="store", help=None, type=str, choices=None,
        nargs=None, metavar=None, dest=None, default=None, const=None):
    
    ret = {
        "action": action,
        "nargs": nargs,
        "default": default,
        "type": type,
        "choices": choices,
        "required": False,
        "help": help,
        "metavar": metavar,
        "dest": dest,
        "nargs": nargs,
        "kind": "opt"
    }
    
    
    # if short is not None:
    #     ret["flags"] = "-" + short
    
    return ret


def flag(short=None, action="store_true", help=None, dest=None):

    ret = {
        "action": action,
        "help": help,
        "dest": dest,
        "kind": "flag"
    }
    
    
    # if short is not None:
    #     ret["flags"] = "-" + short
    
    return ret


def annot(**kwargs):
    parent = kwargs.pop("parent", None)
    
    def annotate(f):
        f.__parent__ = parent
        f.__annotations__ = kwargs
        
        return f
        
    return annotate


class CParse(object):
    def __init__(self, **kwargs):
        self.argp, self.args = ArgumentParser(**kwargs), None
        
        for key, value in self.__init__.__annotations__.items():
            if value.pop("kind") == "pos":
                self.argp.add_argument(key, **value)
            else:
                self.argp.add_argument(self.prefix_char + key, **value)
            
        self.subparser = self.argp.add_subparsers(**kwargs)
        
        try:
            cmds = self.commands
        except AttributeError:
            return
        
        for cmd in cmds:
            fun = getattr(self, cmd)
            subp = self.subparser.add_parser(fun.__name__)
            
            try:
                parent = fun.__parent__
            except AttributeError:
                parent = None
            
            if parent is not None:
                fun.__annotations__.update(getattr(self, parent).__annotations__)
            
            
            for key, value in fun.__annotations__.items():
                if value.pop("kind") == "pos":
                    subp.add_argument(key, **value)
                else:
                    subp.add_argument("--" + key, **value)
            
            subp.set_defaults(fun=fun)
    
    
    def __getitem__(self, item):
        return getattr(self.args, item)
    
    
    def parse(self):
        self.args = self.argp.parse_args()
        return self


def isiter(obj):
    return isinstance(obj, Iterable)


def new_type(type_name, field_names):
    if isinstance(field_names, str_t):
        # names separated by whitespace and/or commas
        field_names = field_names.replace(',', ' ').split()
    
    check_name(type_name)
    seen_fields = set()
    
    for name in field_names:
        check_name(name)
        
        if name in seen_fields:
            raise ValueError('Encountered duplicate field name: %r' % name)
        
        seen_fields.add(name)
    
    def derive(*names):
        def inner(cls):
            return new_type(cls.__name__, field_names + names)
        
        return inner
            
            
    
    return type(
        type_name,
        (PlainBase,),
        {
            "__slots__": field_names,
            "__init__": make_constructor(field_names),
            "derive": derive,
        }
    )


class PlainBase(object):
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return all(i == j for i, j in zip(self, other))

    def __iter__(self):
        for name in self.__slots__:
            yield getattr(self, name)

    def __repr__(self):
        values = tuple(self)
        return self.__class__.__name__ + repr(values)

    def to_dict(self):
        return OrderedDict(zip(self.__slots__, self))


def make_constructor(fields):
    assignments = '\n'.join(['    self.{0} = {0}'.format(f) for f in fields])
    parameter_lists = ', '.join(fields)
    source = 'def __init__(self, %s):\n%s' % (parameter_lists, assignments)
    namespace = {}
    exec(source, namespace)
    return namespace['__init__']


def check_name(name: str):
    if not all(c.isalnum() or c == '_' for c in name):
        raise ValueError("Type names and field names can only contain "
                         "alphanumeric characters and underscores: %r" % name)
    if iskeyword(name):
        raise ValueError("Type names and field names "
                         "cannot be a keyword: %r" % name)
    if name[0].isdigit():
        raise ValueError("Type names and field names cannot start with a "
                         "number: %r" % name)


def make_applyer(function):
    def inner(self, fun, *args, **kwargs):
        f = ft.partial(fun, *args, **kwargs)
        return Seq(function(f, self))
    
    return inner


lazy = 1

class Seq(object):
    __slots__ = ("_seq",)
    
    processes = -1
    parallel = processes >= 0
    
    if parallel:
        pool = Pool(processes)
    
    
    if lazy:
        def __init__(self, arg):
            self._seq = arg
    else:
        def __init__(self, *args, **kwargs):
            self._seq = tuple(*args, **kwargs)
    
    
    def __iter__(self):
        return iter(self._seq)
    
    def __getitem__(self, item):
        if isinstance(item, slice):
            return Seq(islice(self, item.start, item.stop, item.step))
    
    
    def __str__(self):
        return str(self._seq)
    
    
    def __repr__(self):
        return repr(self._seq)
    
    
    def tup(self):
        return tuple(self)
    
    
    def tee(self, n=2):
        return (Seq(itered) for ii in range(n))
    
    # map = make_applyer(map)
    #filter = make_applyer(filter)
    #filter_false = make_applyer(filterfalse)
    #reduce = make_applyer(reduce)
    
    def map(self, fun, *args, **kwargs):
        return Seq(map(ft.partial(fun, *args, **kwargs), self))
    
    
    if parallel:
        if lazy:
            def pmap(self, fun, *args, **kwargs):
                return Seq(self.pool.imap(ft.partial(fun, *args, **kwargs), 
                                          self))
        else:
            def pmap(self, fun, *args, **kwargs):
                return Seq(self.pool.map(ft.partial(fun, *args, **kwargs), 
                                         self))
    
    
    def omap(self, fun, *args, **kwargs):
        return self.map(op.methodcaller(fun, *args, **kwargs))
    
    def select(self, field):
        return self.map(op.attrgetter(field))
    
    def chain(self):
        return Seq(chain.from_iterable(self))
    
    def reduce(self, fun):
        return Seq(reduce(fun, self))
    
    def filter(self, fun, *args, **kwargs):
        return Seq(filter(ft.partial(fun, *args, **kwargs), self))

    def filter_false(self, fun, *args, **kwargs):
        return Seq(filterfalse(ft.partial(fun, *args, **kwargs), self))
    
    def sum(self, init=0):
        return Seq(sum(self, init))
    
    def sorted(self, key=None):
        return sorted(self, key=key)
    
    def str(self):
        return self.map(str)
    
    def join(self, txt):
        return txt.join(self)
    
    def takewhile(fun):
        return Seq(takewhile(fun, self))
    
    def take(self, *args):
        return Seq(islice(self, *args))
    
    def any(self):
        return any(self)

    def all(self):
        return all(self)
    
    def enum(self, **kwargs):
        return enumerate(self, **kwargs)


"""Python module for generating .ninja files.

Note that this is emphatically not a required piece of Ninja; it's
just a helpful utility for build-file-generation systems that already
use Python.
"""

import re
import textwrap

def escape_path(word):
    return word.replace('$ ', '$$ ').replace(' ', '$ ').replace(':', '$:')


home = pth.join("/", "home", "istvan")

class Ninja(object):
    def __init__(self, output, width=78):
        self.output = output
        self.width = width
    
    def __del__(self):
        self.close()

    def newline(self):
        self.output.write('\n')

    def comment(self, text):
        for line in textwrap.wrap(text, self.width - 2, break_long_words=False,
                                  break_on_hyphens=False):
            self.output.write('# ' + line + '\n')

    def variable(self, key, value, indent=0):
        if value is None:
            return
        if isinstance(value, list):
            value = ' '.join(filter(None, value))  # Filter out empty strings.
        self._line('%s = %s' % (key, value), indent)

    def pool(self, name, depth):
        self._line('pool %s' % name)
        self.variable('depth', depth, indent=1)

    def rule(self, name, command, description=None, depfile=None,
             generator=False, pool=None, restat=False, rspfile=None,
             rspfile_content=None, deps=None):
        self._line('rule %s' % name)
        self.variable('command', command, indent=1)
        if description:
            self.variable('description', description, indent=1)
        if depfile:
            self.variable('depfile', depfile, indent=1)
        if generator:
            self.variable('generator', '1', indent=1)
        if pool:
            self.variable('pool', pool, indent=1)
        if restat:
            self.variable('restat', '1', indent=1)
        if rspfile:
            self.variable('rspfile', rspfile, indent=1)
        if rspfile_content:
            self.variable('rspfile_content', rspfile_content, indent=1)
        if deps:
            self.variable('deps', deps, indent=1)

    def build(self, outputs, rule, inputs=None, implicit=None, order_only=None,
              variables=None, implicit_outputs=None, pool=None):
        outputs = as_list(outputs)
        out_outputs = [escape_path(x) for x in outputs]
        all_inputs = [escape_path(x) for x in as_list(inputs)]

        if implicit:
            implicit = [escape_path(x) for x in as_list(implicit)]
            all_inputs.append('|')
            all_inputs.extend(implicit)
        if order_only:
            order_only = [escape_path(x) for x in as_list(order_only)]
            all_inputs.append('||')
            all_inputs.extend(order_only)
        if implicit_outputs:
            implicit_outputs = [escape_path(x)
                                for x in as_list(implicit_outputs)]
            out_outputs.append('|')
            out_outputs.extend(implicit_outputs)

        self._line('build %s: %s' % (' '.join(out_outputs),
                                     ' '.join([rule] + all_inputs)))
        if pool is not None:
            self._line('  pool = %s' % pool)

        if variables:
            if isinstance(variables, dict):
                iterator = iter(variables.items())
            else:
                iterator = iter(variables)

            for key, val in iterator:
                self.variable(key, val, indent=1)

        return outputs

    def include(self, path):
        self._line('include %s' % path)

    def subninja(self, path):
        self._line('subninja %s' % path)

    def default(self, paths):
        self._line('default %s' % ' '.join(as_list(paths)))

    def _count_dollars_before_index(self, s, i):
        """Returns the number of '$' characters right in front of s[i]."""
        dollar_count = 0
        dollar_index = i - 1
        while dollar_index > 0 and s[dollar_index] == '$':
            dollar_count += 1
            dollar_index -= 1
        return dollar_count

    def _line(self, text, indent=0):
        """Write 'text' word-wrapped at self.width characters."""
        leading_space = '  ' * indent
        while len(leading_space) + len(text) > self.width:
            # The text is too wide; wrap if possible.

            # Find the rightmost space that would obey our width constraint and
            # that's not an escaped space.
            available_space = self.width - len(leading_space) - len(' $')
            space = available_space
            while True:
                space = text.rfind(' ', 0, space)
                if (space < 0 or
                    self._count_dollars_before_index(text, space) % 2 == 0):
                    break

            if space < 0:
                # No such space; just use the first unescaped space we can find.
                space = available_space - 1
                while True:
                    space = text.find(' ', space + 1)
                    if (space < 0 or
                        self._count_dollars_before_index(text, space) % 2 == 0):
                        break
            if space < 0:
                # Give up on breaking.
                break

            self.output.write(leading_space + text[0:space] + ' $\n')
            text = text[space+1:]

            # Subsequent lines are continuations, so indent them.
            leading_space = '  ' * (indent+2)

        self.output.write(leading_space + text + '\n')
    
    def close(self):
        self.output.close()
    
    # Own additions
        
    @staticmethod
    def out(infile, **kwargs):
        ext = kwargs.get("ext", None)
        outdir = kwargs.get("outdir", "build")
        
        ret = pth.join(outdir, pth.splitext(pth.basename(infile))[0])
        
        if ext is not None:
            ret += ext
        
        return ret

    
class HTML(Ninja):
    gpp_include = pth.join(home, "Dokumentumok", "texfiles", "gpp")
    
    gpp_flags = (
        '--nostdinc -I%s -U "\\\\" "" "{" "}{" "}" "{" "}" "#" "" '
        '+c "/*" "*/" +c "%%" "\\n" -x'
    ) % gpp_include
    
    ext = ".html"
    
    def __init__(self, path="build.ninja", **kwargs):
        
        Ninja.__init__(self, open(path, "w"), **kwargs)
        
        self.rule("html", "gpp %s -o $out $in " % self.gpp_flags,
                  "html preprocessing", **kwargs)
        self.newline()
    
    def sources(self, sources, **kwargs):
        for src in sources:
            out = HTML.out(src, ext=self.ext, **kwargs)
            self.build(out, "html", inputs=src)
            self.newline()
    
    def full(self, sources, **kwargs):
        infile = "full.cml"
        out = HTML.out(infile, ext=self.ext, **kwargs)
        
        self.build(out, "html", inputs=infile, implicit=sources)
        self.newline()

eset = set()

class Compiled(Ninja):
    obj_ext = ".o"
    
    # TODO: change it in case of Windows OS
    exe_ext = None
    
    def __init__(self, **kwargs):
        path = kwargs.pop("path", "build.ninja")
        
        inc_dirs = set(kwargs.pop("inc_dirs", eset))
        link_dirs = set(kwargs.pop("link_dirs", eset))
        defines = set(kwargs.pop("defines", eset))
        link_flags = set(kwargs.pop("link_flags", eset))
        compile_flags = set(kwargs.pop("compile_flags", eset))
        
        Ninja.__init__(self, open(path, "w"), **kwargs)
        
        
        compile_cmd = \
        "{compiler} {compiler_flags} {inc_dirs} {defines} -c "\
        "-o ${{out}} ${{in}}"\
        .format(
            compiler=self.compiler,
            inc_dirs=" ".join("-I" + elem for elem in inc_dirs),
            compiler_flags=" ".join(self.compile_flags | compile_flags),
            defines=" ".join(map(proc_define, defines))
        )
        
        self.rule("compile_object", compile_cmd,
                  "Compiling object ${out}.")
        self.newline()
        
        link_cmd = \
        "{compiler} ${{in}} {link_flags} {link_dirs} -o ${{out}}"\
        .format(
            compiler=self.compiler,
            link_dirs=" ".join("-L" + elem for elem in link_dirs),
            link_flags=" ".join(link_flags)
        )
        
        # TODO: make a specialized message for linking and creating an
        # executable
        self.rule("link", link_cmd, "Linking executable ${out}.")
        self.newline()
    
    
    def obj(self, source, **kwargs):
        out = self.out(source, ext=self.obj_ext)
        self.build(out, "compile_object", inputs=source, **kwargs)
        self.newline()
        
        return out
    
    
    def exe(self, source, **kwargs):
        depends = kwargs.pop("depends", None)
        outdir = kwargs.pop("outdir", "bin")
        
        src = as_list(source)
        
        if depends is not None:
            src += as_list(depends)
        
        
        
        out = self.out(source, ext=self.exe_ext, outdir=outdir)
        self.build(out, "link", inputs=src, **kwargs)
        self.newline()


class C(Compiled):
    gcc_debug_flags = {
        "-Werror -Wall -Wextra -Wfloat-equal -Wundef -Wshadow -Wpointer-arith "
        "-Wcast-align -Wstrict-prototypes -Wstrict-aliasing "
        "-Wstrict-overflow=5 -Wwrite-strings -Wcast-qual -Wswitch-default "
        "-Wconversion -Wunreachable-code -O0"
    }
    
    def __init__(self, **kwargs):
        # mode = kwargs.pop("mode", "debug")
        
        standard = kwargs.pop("std", None)
        
        self.compiler = "gcc"
        
        flags = eset

        if standard is not None:
            assert standard in {"89", "99"}
            flags.add("-std=c%s" % standard)

        self.compile_flags = flags
        self.link_flags = {"-lm",}
        
        Compiled.__init__(self, **kwargs)
        

class Cpp(Compiled):
    gcc_debug_flags = C.gcc_debug_flags | {"-Weffc++",}
    
    def __init__(self, **kwargs):
        # mode = kwargs.pop("mode", "debug")
        
        standard = kwargs.pop("std", None)
        
        self.compiler = "gcc"
        
        flags = self.gcc_debug_flags

        if standard is not None:
            assert standard in {"98", "03", "11", "14", "17", "20"}
            flags.add("-std=c++%s" % standard)

        self.compile_flags = flags
        self.link_flags = {"-lstc++", "-lm"}
        
        Compiled.__init__(self, **kwargs)

def as_list(input):
    if input is None:
        return []
    if isinstance(input, (list, tuple)):
        return input
    return [input]


def escape(string):
    """Escape a string such that it can be embedded into a Ninja file without
    further interpretation."""
    assert '\n' not in string, 'Ninja syntax does not allow newlines'
    # We only have one special metacharacter: '$'.
    return string.replace('$', '$$')


def expand(string, vars, local_vars={}):
    """Expand a string containing $vars as Ninja would.

    Note: doesn't handle the full Ninja variable syntax, but it's enough
    to make configure.py's use of it work.
    """
    def exp(m):
        var = m.group(1)
        if var == '$':
            return '$'
        return local_vars.get(var, vars.get(var, ''))
    
    return re.sub(r'\$(\$|\w*)', exp, string)


def proc_define(elem):
    try:
        return "-D%s=%s" %(elem[0], elem[1])
    except TypeError:
        return "-D%s" % elem
    
def reext(path, ext):
    return pth.splitext(path)[0] + ext
