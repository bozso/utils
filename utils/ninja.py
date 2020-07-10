"""Python module for generating .ninja files.

Note that this is emphatically not a required piece of Ninja; it's
just a helpful utility for build-file-generation systems that already
use Python.
"""

import re
import textwrap

from utils import Path
import os.path as path

__all__ = (
    "Ninja",
)

def escape_path(word):
    return word.replace('$ ', '$$ ').replace(' ', '$ ').replace(':', '$:')

home = Path.joined("/", "home", "istvan")

class Ninja(object):
    def __init__(self, output, width=78):
        self.output = output
        self.width = width

    @classmethod
    def in_path(cls, *args, **kwargs):
        p = path.join(*args, "build.ninja")
        return cls(open(p, "w"), **kwargs)
    
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
        
        ret = path.join(outdir, path.splitext(path.basename(infile))[0])
        
        if ext is not None:
            ret += ext
        
        return ret

eset = set()

class Dependencies(object):
    __slots__ = ("pattern", "include_paths", "files")
    
    def __init__(self, *args, **kwargs):
        self.pattern, self.include_paths, self.files = \
        kwargs["pattern"], kwargs["include_paths"], eset
    
    def search_file(self, Path):
        for p in self.include_paths:
            f = path.join(p, Path)
            
            # print(f, pth.isfile(f))
            
            if path.isfile(f):
                return f
        
        return None
    
    def clear(self):
        self.files.clear()
    
    def get_dependencies(self, path):
        with open(path, "r") as f:
            for line in f:
                m = self.pattern.match(line)
                
                
                if m:
                    g = m.group(1)
                    f = self.search_file(g)
                    
                    if f is None:
                        raise RuntimeError("Could not find '%s' in "
                            "include paths: %s while processing: '%s'" % 
                            (g, self.include_paths, path)
                        )
                    
                    
                    if f in self.files:
                        continue
                    else:
                        self.files.add(f)
                        self.get_dependencies(f)
                    
    
    
class HTML(Ninja):
    __slots__ = ("deps",)
    
    regex_include = re.compile(r"\\include{(\D+)}")
    
    gpp_flags = (
        '--nostdinc -U "\\\\" "" "{" "}{" "}" "{" "}" "#" "" '
        '+c "/*" "*/" +c "#" "\\n" -x'
    )
    
    cmd_tpl = "gpp {include_dirs} {flags} -o ${{out}} ${{in}} "
    
    ext = ".html"
    
    _include_dirs = {home.join("Dokumentumok", "texfiles", "gpp"),}
    
    def __init__(self, *args, **kwargs):
        include_dirs = \
        self._include_dirs | kwargs.pop("include_dirs", eset)
        
        self.deps = Dependencies(
            pattern = self.regex_include,
            include_paths = include_dirs
        )
        
        _include_dirs = " ".join(
            "-I%s" % elem for elem in include_dirs
        )
        
        Ninja.__init__(self, *args, **kwargs)
        
        self.rule("html",
            self.cmd_tpl.format(
                flags=self.gpp_flags, include_dirs=_include_dirs
            ),
            "Preprocessing into HTML file.",
            **kwargs
        )
        
        self.newline()
    
        
    def sources(self, sources, **kwargs):
        for src in sources:
            self.deps.include_paths.add(path.abspath(path.dirname(src)))
            
            self.deps.get_dependencies(src)
            
            implicit = kwargs.pop("implicit", eset)
            implicit |= self.deps.files
            
            out = self.out(src, ext=self.ext, **kwargs)
            self.build(out, "html", inputs=src, implicit=list(implicit),
                **kwargs)
            self.newline()

            self.deps.clear()
    
    def full(self, sources, **kwargs):
        infile = "full.cml"
        out = self.out(infile, ext=self.ext, **kwargs)
        
        self.build(out, "html", inputs=infile, implicit=sources)
        self.newline()


class Html(HTML):
    ext = ".build.html"
    
    def out(self, src, **kwargs):
        kwargs.setdefault("outdir", ".")

        return super().out(src, **kwargs)


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
        
        
        compile_cmd = (
            "{compiler} {compiler_flags} {inc_dirs} {defines} -c "
            "-o ${{out}} ${{in}}"
        ).format(
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
