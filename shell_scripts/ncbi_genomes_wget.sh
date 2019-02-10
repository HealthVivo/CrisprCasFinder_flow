#!/bin/bash

#Ian Rambo
#February 9, 2019
#PURPOSE: download genomes from NCBI FTP in parallel.

genomeTable=$1 #file from NCBI containing FTP path(s)
dbDir=$2 #output directory
nJob=$3 #number of simultaneous parallel jobs
joblog=$4 #joblog from gnu parallel

#Script is currently set for Genbank genomes
#==============================================================================
###---MAIN---###
#==============================================================================
#Create the output directory if not present
[[ -d $dbDir ]] || mkdir $dbDir

cd $dbDir
grep -o "ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/[0-9]\{3\}/[0-9]\{3\}/[0-9]\{3\}/GCA_[0-9]\{9\}.[0-9]*[\.\_A-Za-z0-9\-]*" $genomeTable | \
    sed  -r 's|(ftp://ftp.ncbi.nlm.nih.gov/genomes/all/)(GCA/)([0-9]{3}/)([0-9]{3}/)([0-9]{3}/)(GCA_.+)|\1\2\3\4\5\6/\6_genomic.fna.gz|' | \
    sort | \
    uniq | \
    parallel --jobs $nJob --joblog $joblog wget --quiet {}

#Did wget jobs complete successfully?
exitStats=$( tail -n +2 $joblog | awk '$7 != 0' | wc -l )
if [ "$exitStats" -gt 0 ]
then
    echo "WARNING: $exitStats wget jobs exited with errors"
else
    echo "No wget jobs exited with errors"
    echo "DONE"
fi

#Download md5 files and make sure genomes are correct
printf "\n################ Downloading md5sum ###############\n"

awk '{FS=","} {print $15}' ${genomeTable} | grep 'ftp' - | parallel --no-notice --jobs ${nJob} --joblog md5sum.log wget -q -O - {}/md5checksums.txt | grep "_protein.faa.gz" >> ${genomeTable}_md5sum.out
printf "\n################ Download finished ###############\n"
printf "\n################ Verifying downloaded files using  md5sum ###############\n"

# verification of downloaded files
md5sum --quiet -c ${genomeTable}_md5sum.out > ../md5sumchk.out

if [ -s "../md5sumchk.out" ]
then
    printf "\n WARNING !! Some downloaded files were not OK. Check md5sumchk.out for the list of filenames \n"
else
    printf "\n Downloaded files verified. All OK ! \n"
fi

exit 0
