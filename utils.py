import functools as ft
import os
import operator as op
from itertools import tee, takewhile, islice, chain, filterfalse
from collections.abc import Iterable
from os import path as pth
from errno import EEXIST
from tempfile import _get_default_tempdir, _get_candidate_names
from shutil import copyfileobj
from argparse import ArgumentParser
from glob import iglob
from sys import version_info
from keyword import iskeyword
from collections import OrderedDict
from copy import copy


__all__ = (
    "new_type",
    "str_t",
    "Seq",
    "fun",
    "ls",
    "isiter",
    "all_same",
    "make_object",
    "make_join",
    "Params",
    "tmp_file",
    "get_par",
    "cat",
    "Files",
    "Multi",
    "Base",
    "CParse",
    "annot",
    "pos",
    "opt",
    "flag",
    "rm",
    "ln",
    "mv",
    "mkdir",
    "compose",
    "isfile",
    "fs"
)


py3 = version_info[0] == 3


if py3:
    str_t = str,
else:
    str_t = basestring,


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


class Cache(object):
    
    def __init__(self, root):
        self.root = mkdir(root)
        
        mk = compose(mkdir, ft.partial(pth.join, root))
        
        self.unzip, self.slc, self.rslc, self.ifg = \
        mk("unzip"), mk("slc"), mk("rslc"), mk("ifg")
    
    
    def join(self, *args, **kwargs):
        return pth.join(self.root, *args, **kwargs)
    
    
    def dir(self, name):
        return Cache(mkdir(self.join(name)))


    def list(self, name):
        if not pth.isdir(self.join(name)):
            return empty_iter
        else:
            return iglob(self.join(name, "*"))
    

    
def all_same(iterable, fun=None):
    if fun is not None:
        n = len(set(tee(map(fun, iterable),1)))
    else:
        n = len(set(tee(iterable,1)))
    
    return n == 1


def make_object(name, inherit=(object,), **kwargs):
    return type(name, inherit, **kwargs)



class Params(object):
    def __init__(self, dictionary):
        self.params = dictionary
    
    @classmethod
    def from_file(cls, path, sep=":"):
        with open(path, "r") as f:
            return cls({
                line.split(sep)[0].strip() : " ".join(line.split(sep)[1:]).strip()
                for line in f if line
            })
    
    def __str__(self):
        return pformat(self.params)
    
    def __getitem__(self, key):
        return self.params[key]

    def float(self, key, idx=0):
        return float(self[key].split()[idx])

    def int(self, key, idx=0):
        return int(self[key].split()[idx])


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


def mkdir(path):
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

            
def make_join(path):
    def f(*args, **kwargs):
        return pth.join(path, *args, **kwargs)
    
    return f


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
                self.argp.add_argument("--" + key, **value)
            
        
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


class Fun(object):
    def __init__(self, fun):
        self.fun = fun
    
    def __call__(self, *args, **kwargs):
        return self.fun(*args, **kwargs)
    
    def __getitem__(self, *args, **kwargs):
        return Fun(ft.partial(self.fun, *args, **kwargs))
    
    def __lt__(self, other):
        return Fun(compose(self.fun, other.fun))
    
    def __rlt__(self, other):
        return Fun(compose(other.fun, self.fun))
    
    def __str__(self):
        return str(self.fun)


fun = Fun

def make_applyer(function):
    def inner(self, fun, *args, **kwargs):
        f = ft.partial(fun, *args, **kwargs)
        return Seq(function(f, self))
    
    return inner


class Seq(object):
    __slots__ = ("_seq",)
    
    def __init__(self, *items):
        assert len(items) > 0
        
        zero = items[0]
        
        if isinstance(zero, Seq):
            self._seq = zero.seq
        elif isinstance(zero, Iterable) \
             and not isinstance(zero, str_t):
            self._seq = zero
        else:
            self._seq = items
                
    def __iter__(self):
        return iter(self._seq)
    
    
    def __getitem__(self, item):
        if isinstance(item, slice):
            return Seq(islice(self, item.start, item.stop, item.step))
    
    def tee(self, n=2):
        itered = tuple(self)
        return (Seq(itered) for ii in range(n))
    
    map = make_applyer(map)
    #filter = make_applyer(filter)
    #filter_false = make_applyer(filterfalse)
    #reduce = make_applyer(reduce)
    
    #def map(self, fun, *args, **kwargs):
    #    return Seq(map(ft.partial(fun, *args, **kwargs), self))
    
    def seq(self):
        return Seq(self.collect())
    
    def omap(self, fun, *args, **kwargs):
        return self.map(ft.partial(op.methodcaller(fun), *args, **kwargs))
    
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
    
    def collect(self, collection=tuple):
        return collection(self)
    
    def any(self):
        return any(self)

    def all(self):
        return all(self)

        
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
    
    return type(
        type_name,
        (PlainBase,),
        {
            '__slots__': field_names,
            '__init__': make_constructor(field_names)
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


def check_name(name):
    if not all(c.isalnum() or c == '_' for c in name):
        raise ValueError("Type names and field names can only contain "
                         "alphanumeric characters and underscores: %r" % name)
    if iskeyword(name):
        raise ValueError("Type names and field names "
                         "cannot be a keyword: %r" % name)
    if name[0].isdigit():
        raise ValueError("Type names and field names cannot start with a "
                         "number: %r" % name)
