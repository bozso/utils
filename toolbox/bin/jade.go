package main

import (
    "fmt"
    "os"
    "flag"
    "io"
    "io/ioutil"
    "html/template"
    //"github.com/Joker/hpp" // Prettify HTML
    "github.com/Joker/jade"
)

func main_jade() error {
    fl := flag.NewFlagSet("jade", flag.ContinueOnError)
    
    var infile, outfile string
    fl.StringVar(&infile, "infile", "", "Input jade file")
    fl.StringVar(&outfile, "outfile", "-", "Output html file")
    
    if err := fl.Parse(os.Args[2:]); err != nil {
        return fmt.Errorf("failed to parse command line arguments")
    }
    
    inf, err := os.Open(infile)
    if err != nil {
        return fmt.Errorf("failed to open file '%s': %v\n", infile, err)
    }
    defer inf.Close()
    
    b, err := ioutil.ReadAll(inf)
    if err != nil {
        return fmt.Errorf("failed to read file '%s': %v\n", infile, err)
    }
    
    txt, err := jade.Parse("", b)
    if err != nil {
        return fmt.Errorf("Parse error: %v\n", err)
    }
    
    tpl, err := template.New("").Parse(txt)
    if err != nil {
        return fmt.Errorf("Parse error: %v\n", err)
    }
    
    var outf io.Writer
    if outfile == "-" {
        outf = os.Stdout
    } else {
        if outf, err = os.Create(outfile); err != nil {
            return fmt.Errorf("failed to open file '%s': %w",
                outfile, err)
        }
    }
    
    if err := tpl.Execute(outf, nil); err != nil {
        return err
    }
    
    return nil
}
