package toolbox

import (
    "os/exec"
)

type gnuplotConfig struct {
    Persist, Debug, Silent bool
    Exe, Dim2, Dim3 string
    Size [2]int
}

const (
    defaultDim2 = 
`
set style line 11 lc rgb 'black' lt 1
set border 3 back ls 11 lw 2.5
set tics nomirror
set style line 12 lc rgb 'black' lt 0 lw 1
set grid back ls 12 lw 2.0
`,
    defaultDim3 = 
`
set style line 11 lc rgb 'black' lt 1
set border 3 back ls 11 lw 2.5
set tics nomirror
set style line 12 lc rgb 'black' lt 0 lw 1
set grid back ls 12 lw 2.0
`
)

func NewConfig() gnuplotConfig {
    return gnuplotConfig{
        Persist : false,
        Silent : false,
        Debug : false,
        Exe : "gnuplot",
        Size : [2]int{800, 600},
        Dim2 : defaultDim2,
        Dim3 : defaultDim3,
    }
}

type Instance struct {
    Config gnuplotConfig
    Figures []Figure
}

type Axe struct {
    name string
}

type Figure struct {
    
    
}
