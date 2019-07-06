from base import cmd
from os.path import join


__all__ = (
    "run",
    "start_server",
    "new_session",
    "send_keys",
    "cd",
    "split_window",
    "select_pane",
    "list_sessions"
)


bin = "tmux"


def run(*args, **kwargs):
    cmd(bin, *args, **kwargs)


def start_server():
    run("start-server")


def new_session(name, **kwargs):
    run("new-session", "-d", "-t %s" % name, **kwargs)


def send_keys(*args, **kwargs):
    run("send-keys", *args, "C-m", **kwargs)


def cd(path, *args, **kwargs):
    send_keys("cd %s" % join(*args))


def split_window(*args, **kwargs):
    path = kwargs.pop("path")
    
    if path is not None:
        args.append("-c %s" % join(path))
    
    type = kwargs.pop("type")
    
    if type in ("h", "horizontal"):
        args.append["-h"]
    elif type in ("v", "vertical"):
        args.append["-v"]
    
    run(*args, **kwargs)


def select_pane(num, *args, **kwargs):
    run("select-pane", "-t %d" % num, *args, **kwargs)


def list_sessions(*args, **kargs):
        pass


