#!/usr/bin/env bash

projname=$1
workdir=$2
outdir=$3

clusterfile=${outdir}/casClusters_ccFinder_${projname}.txt

printf "Sequence\tCluster_Id\tNb\tCRISPRs\tNb\tCas\tStart\tEnd\tDescription" > $clusterfile
find ${workdir}/batch-*-crisprCasFinder-${projname}/Result*/TSV -name "CRISPR-Cas_clusters.tsv" ! -size 0 -exec grep -e "[0-9]" {} > $clusterfile \;

casreport=${outdir}/casReport_ccFinder_${projname}.gff
find ${workdir}/batch-*-crisprCasFinder-${projname}/Result*/Prodigal -type f -name "*.faa" ! -size 0 -exec cat {} > $casreport \;
