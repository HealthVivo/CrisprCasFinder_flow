#!/bin/bash
#Parse fasta sequences of Cas genes from Prodigal output using Cas report gff3
#from CrisprCasFinder

#CrisprCasFinder Cas Report
casReport=$1
#FASTA file to pull sequences from
fastaFile=$2
#Working directory
workingDir=$3
#Project name prefix to give output files
projectName=$4

 for i in $( awk '{print $2}' $casReport | sort -k1 | uniq ); do
     outfile=$workingDir/${i}_${projectName}_prodigalSeqs.faa; touch $outfile;
     seqids=$( grep -v forbidden $casReport | \
     awk '{print $1,$2}' | \
     grep "$i" | \
     awk '{print $1}' );

     for s in $seqids; do
         sed -n "/>$s\s/,/^>/ p" $ fastaFile | sed \$d >> $outfile;
     done;
 done;
 echo FINISHED
