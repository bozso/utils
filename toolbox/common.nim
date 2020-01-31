import osproc, strformat, strutils

type
  ProcErr = object of Exception


type
  Command = object
    cmd: string
    

proc initCmd*(command: string): Command =
  result.cmd = command

let errTpl =
  """
  \nNon zero returncode from command: \n'${Cmd}'
  \nOUTPUT OF THE COMMAND: \n\n$#
  \nRETURNCODE was: $#
  """

proc cmd(cmd: Command, args: varargs[string, `$`],
         debug: bool = false): string =
    
    let
      arg = args.join(" ")
      Cmd = fmt"{cmd.cmd} {arg}"
    
    if debug:
      echo fmt"Command is '{Cmd}'"

      return
    
    try:
        result = execProcess(Cmd, args = args)
    except Exception as e:
        when false:
          raise newException(ProcErr)
        else:
          raise
