from subprocess import check_output, CalledProcessError, STDOUT
from shlex import split

def cmd(Cmd, debug=False):
    """
    Calls a command line program. See documentation of modules for arguments.
    
    Parameters
    ----------
    Cmd : str
        Command string to be executed.
    
    Returns
    -------
    ret : byte-string
        Output of called module.
    
    Raises
    ------
    CalledProcessError
        If something went wrong with the calling of the module, e.g.
        non zero returncode.

    Examples
    --------
    
    >>> from utils.git import cmd
    >>> cmd("ls *.png *.txt")
    """
    
    if debug:
        print(Cmd)
        return None
    
    try:
        cmd_out = check_output(split(Cmd), stderr=STDOUT)

    except CalledProcessError as e:
        print("ERROR: Non zero returncode from command: '{}'".format(Cmd))
        print("OUTPUT OF THE COMMAND: \n{}".format(e.output.decode()))
        print("RETURNCODE was: {}".format(e.returncode))
        
        raise e
        
    return cmd_out
