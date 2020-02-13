import utils

home = utils.Path.joined("/home", "istvan")
progs = home.join(home, "progs")
github = progs.join("github.com")
bitbucket = progs.join("bitbucket.org")


notify_send = utils.Command.with_parser("notify-send")

def notify(msg, header=None, icon=None, time=None):
    
    if header is not None:
        txt = '"%s" "%s"' % (header, msg)
    else:
        txt = msg
    
    if icon is not None:
        txt = '%s -i "%s"' % (txt, join(icons, icon))
    
    if time is not None:
        txt = "%s -t %s" % (txt, time)
    
    return notify_send(txt)


def debug(msg):
    notify(msg, header="Debug", icon="debug.png")
