package toolbox

import (
    "log"
)

func fatal(err Error, msg string, args ...interface{}) {
    if err != nil {
        log.Fatalf(msg, args)
    }
}
