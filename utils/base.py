import sys
import functools as ft
import json

__all__ = (
    "Seq", "flat", "new_type", "str_t", "isiter", "all_same",
    "make_object", "cat", "compose", "fs", "load", "Enum", "namespace",
    "export", "JSONSave", "separate_options",
)

py3 = sys.version_info[0] == 3


from collections.abc import Iterable
    

if py3:
    str_t = str
else:
    str_t = basestring

def export(fn):
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]
    return fn

def flat(arg):
    return tup(chain.from_iterable(map(tup, arg)))

def fs(*elems):
    return frozenset(elems)

def compose2(f, g):
    return lambda *a, **kw: f(g(*a, **kw))
    
def compose(*functions):
    return ft.reduce(compose2, functions)

def namespace(**kwargs):
    name, inh = (
        kwargs.pop("_name_", "namespace"),
        kwargs.pop("_inherit_", (object,))
    )
    
    return type(name, inh, kwargs)


class Enum(object):
    def __init__(self, *sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        self.__dict__.update(enums)
    
    def unwrap(self, prefix=""):
        d = dict()
        
        if prefix != "":
            prefix = "%s_" % prefix 
        
        for key, val in self.items():
            if isinstance(val, Enum):
                d.update(val.unwrap(prefix=key))
            else:
                d[prefix + key] = val
        
        return d
    
    def items(self):
        return self.__dict__.items()


empty_iter = iter([])

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


from importlib.machinery import SourceFileLoader

def load(name, path):
    return SourceFileLoader(name, path).load_module()


class JSONSave(object):

    class Encoder(json.JSONEncoder):
        def default(self, obj):
            try:
                return {
                    key: getattr(obj, key)
                    for key in obj.json_serialize
                }
            except AttributeError:
                return json.JSONEncoder.default(self, obj)    
    

    json_options = {
        "indent": 4,
        "cls": Encoder,
    }
    
    def save_to(self, path, **kwargs):
        with open(path, "w") as f:
            self.save(f)
    
    @staticmethod
    def save_any(obj, writable, **kwargs):
        try:
            kwargs.update(obj.json_options)
        except AttributeError:
            kwargs.update(JSONSave.json_options)
        
        json.dump(obj, writable, **kwargs)
        
    
    def save(self, writable, **kwargs):
        self.save_any(self, writable, **kwargs)
    
    @classmethod
    def from_dict(cls, d, *args, **kwargs):
        ret = cls(*args, **kwargs)
        
        for key in cls.json_serialize:
            try:
                val = d[key]
            except KeyError:
                val = None
            
            setattr(ret, key, val)
        
        return ret
    
    @classmethod
    def load_from(cls, path, *args, **kwargs):
        ret = cls(*args, **kwargs)
        
        with open(path, "r") as f:
            ret.load(f, **kwargs)
        
        return ret
        
    def load(self, readable, **kwargs):
        kwargs.update(self.json_options)
        
        self = json.load(self, readable, **kwargs)
    
    @classmethod
    def tree_from(cls, path, *args, **kwargs):
        with open(path, "r") as f:
            return cls.load_tree(f, *args, **kwargs)
    
    @classmethod
    def load_tree(cls, readable, *args, **kwargs):
        d = json.load(readable, **kwargs, **self.json_options)
        
        dd = {}
        for key, val in d.items():
            if isinstance(val, dict):
                dd[key] = cls.from_dict(val, *args, **kwargs)
            else:
                dd[key] = tuple(
                    cls.from_dict(elem, *args, **kwargs)
                    for elem in val
                )
        
        return namespace(**dd)
    
def separate_options(d, key, tpl = "%s_"):
    txt = tpl % key
    
    keys = tuple(filter(lambda k: k.startswith(txt), d.keys()))
    
    r = {}
    
    for key in keys:
        r[key.lstrip(txt)] = d[key]
    
    for key in keys:
        del d[key]
    
    return r
    
