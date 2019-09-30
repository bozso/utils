package tools

import (
    "fmt"
    "os"
    test "testing";
    fp "path/filepath"
)


type String string

func Handle(err error, format string, args ...interface{}) error {
	str := fmt.Sprintf(format, args...)

	if err == nil {
		return fmt.Errorf("%s\n", str)
	} else {
		return fmt.Errorf("%s\n%w", str, err)
	}
}


func (s String) Join(args ...string) String {
	arg := append([]string{string(s)}, args...)
	return String(fp.Join(arg...))
}

func (s String) Empty() bool {
	return len(s) == 0
}

func (s String) Glob() (ret []string, err error) {
	path := string(s)
	ret, err = fp.Glob(path)

	if err != nil {
		err = Handle(err, "Could not execute glob on '%s'!", path)
		return
	}
	return ret, nil
}

func (s String) Stat() (ret os.FileInfo, err error) {
	path := string(s)
	ret, err = os.Stat(path)

	if err != nil {
		err = Handle(err, "Failed to get FileInfo of '%s'", path)
		return
	}
	return ret, nil
}

func (s String) Exist() (ret bool, err error) {
	path := string(s)
	_, err = os.Stat(path)

	if err != nil {
		if os.IsNotExist(err) {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

func Empty(s string) bool {
    return len(s) == 0
}

const (
    nIter = 50000
)

func BenchmarkNativeString(b *test.B) {
    
    b.ReportAllocs();
    
    path := "/home/istvan/"
    
    for ii := 0; ii < nIter; ii++ {
        _, err := os.Stat(fp.Join(path, "progs", "gamma", "gamma", "utils.go"))
        
        if err != nil {
            b.Fatalf("Failed to get stat! %w", err)
        }
        
        ok := Empty("")
        
        if !ok {
            b.Fatalf("Empty string should be empty!")
        }
    }
}

func BenchmarkNewString(b *test.B) {
    
    b.ReportAllocs();
    
    path := String("/home/istvan/")
    
    for ii := 0; ii < nIter; ii++ {
        _, err := path.Join("progs", "gamma", "gamma", "utils.go").Stat()
        
        if err != nil {
            b.Fatalf("Failed to get stat! %w", err)
        }
        
        ok := String("").Empty()
        
        if !ok {
            b.Fatalf("Empty string should be empty!")
        }
    }
}
