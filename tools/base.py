from subprocess import check_output, CalledProcessError, STDOUT
from shlex import split
from os.path import join


__all__ = (
    "repos",
    "cmd",
    "notify",
    "debug",
    "home"
)


home = join("/home", "istvan")
progs = join(home, "progs")
utils = join(progs, "utils")
icons = join(utils, "icons")


repos = {
    "insar_meteo": join(progs, "insar_meteo"),
    "geodynamics": join(progs, "geodynamics"),
    "utils": join(progs, "utils"),
    "texfiles": join(home, "Dokumentumok", "texfiles"),
    "pygamma": join(progs, "gamma")
}


def cmd(*args, **kwargs):
    debug = kwargs.pop("debug", False)
    
    Cmd = " ".join(args)
    
    if debug:
        print(Cmd)
        return
    
    try:
        proc = check_output(split(Cmd), stderr=STDOUT)
    except CalledProcessError as e:
        print("\nNon zero returncode from command: \n'{}'\n"
              "\nOUTPUT OF THE COMMAND: \n\n{}\nRETURNCODE was: {}"
              .format(Cmd, e.output.decode(), e.returncode))
        exit(1)
    

    return proc.decode()


def notify(msg, header=None, icon=None, time=None):
    
    if header is not None:
        txt = '"%s" "%s"' % (header, msg)
    else:
        txt = msg
    
    if icon is not None:
        txt = '%s -i "%s"' % (txt, join(icons, icon))
    
    if time is not None:
        txt = "%s -t %s" % (txt, time)
    
    txt = "notify-send %s" % txt

    cmd(txt)


def debug(msg):
    notify(msg, header="Debug", icon="debug.png")
