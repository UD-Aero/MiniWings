#!/bin/bash

if [ "$1" == "-a" ]
  then
    pdflatex Scitech2021_OFWtrim.tex
    bibtex Scitech2021_OFWtrim.aux
    pdflatex Scitech2021_OFWtrim.tex
    pdflatex Scitech2021_OFWtrim.tex
    okular Scitech2021_OFWtrim.pdf -p $2
elif [ "$1" == "-b" ]
  then
    pdflatex Scitech2021_OFWtrim.tex
    bibtex Scitech2021_OFWtrim.aux
    pdflatex Scitech2021_OFWtrim.tex
    pdflatex Scitech2021_OFWtrim.tex
elif [ "$1" == "-v" ]
  then
    okular Scitech2021_OFWtrim.pdf -p $2
else
    echo "INVALID CMD ARG - ERROR TRY AGAIN"
fi
