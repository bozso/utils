#! /usr/bin/env sh

pdflatex --file-line-error-style -shell-escape "$1"
pdflatex --file-line-error-style -shell-escape "$1"
bibtex "$(basename $1).aux"
pdflatex --file-line-error-style -shell-escape "$1"
