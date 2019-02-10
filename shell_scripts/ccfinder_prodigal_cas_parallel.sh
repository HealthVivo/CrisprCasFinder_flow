#!/bin/bash
#Parse fasta sequences of Cas genes from Prodigal output using Cas report gff3
#from CrisprCasFinder
#LET'S MAKE THIS MORE EFFICIENT

#CrisprCasFinder Cas Report
casReport=$1
#FASTA file to pull sequences from
fastaFile=$2
#Working directory
workingDir=$3
#Project name prefix to give output files
projectName=$4

fetch_seq () {
    local header=${1}
    local fastaIn=${2}
    local fastaOut=${3}
    sed -ne "/>$1\s/,/^>/ p" $2 | sed \$d >> $3;
}
