package main

import (
    "os"
    "fmt"
)

func main() {
    args := os.Args
    
    if len(args) < 2 {
        fmt.Printf("Expected at least one argument.\n")
        return
    }
    
    mode := args[1]
    
    var err error
    
    switch mode {
    case "ace":
        err = ace()
    default:
        fmt.Printf("Unrecognized mode: %s\n", mode)
        return
    }

    if err != nil {
        fmt.Printf("Error occurred: %v\n", err)
        os.Exit(-1)
    }
    
    return
}
