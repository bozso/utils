package main

import (
    "fmt"
    "os"
    "flag"
    "io"
    "io/ioutil"
    
    "github.com/yosssi/ace"
)

func ace() error {
    fl := flag.NewFlagSet("ace", flag.ContinueOnError)
    
    var infile, outfile string
    fl.StringVar(&infile, "infile", "", "Input ace template file")
    fl.StringVar(&outfile, "outfile", "-", "Output html file")
    
    if err := fl.Parse(os.Args[2:]); err != nil {
        return fmt.Errorf("failed to parse command line arguments")
    }
    
    var outf io.Writer
    if outfile == "-" {
        outf = os.Stdout
    } else {
        outf, err = os.Create(outfile)
        if err != nil {
            return fmt.Errorf("failed to open file '%s': %w",
                outfile, err)
        }
        defer outf.Close()
    }
    
    tpl, err := ace.Load(
    
    if err := tpl.Execute(outf, nil); err != nil {
        return err
    }
    
    return nil
}
