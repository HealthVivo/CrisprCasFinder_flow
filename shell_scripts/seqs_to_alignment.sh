#!/bin/bash
ARGS=("$@")
seqdir=${ARGS[0]}
aligndir=${ARGS[1]}
alignprog=${ARGS[2]}

###How to use this script: bash seqs_to_alignment.sh <sequence dir> <alignment dir> <mafft|muscle> <dir_1> <dir_2> ... <dir_n>
###dir_1 to dir_n are directories to search for input files
###the first positional parameter is the directory for combined sequence file output
###the second positional parameter is the directory for multiple sequence alignment output

trimal=/home/ninad/Scripts/Trimal/trimAl/source/trimal
#for i in $(find guaymas compChrom-python sfbay_archaea sfbay_bacteria mb_nerr guaymas2018_archaea  -type f -name "*_prodigalSeqs.faa" ! -size 0 -exec basename {} \; | cut -f1 -d'_' | uniq); do
for i in $(find "${ARGS[@]:3}" -type f -name "*_prodigalSeqs.faa" ! -size 0 -exec basename {} \; | cut -f1 -d'_' | uniq); do
    echo "making combined sequence file for ${i}" && \
    comboFasta=${seqdir}/${i}_combined_prodigalSeqs.faa && \
    #cat guaymas/${i}_*prodigalSeqs.faa compChrom-python/${i}_*prodigalSeqs.faa sfbay_archaea/${i}_*prodigalSeqs.faa sfbay_bacteria/${i}_*prodigalSeqs.faa mb_nerr/${i}_*prodigalSeqs.faa guaymas2018_archaea/${i}_*prodigalSeqs.faa > $comboFasta && \
    find "${ARGS[@]:3}" -name "${i}_*prodigalSeqs.faa" -type f -exec cat {} \; > $comboFasta && \
    comboFastaUAmbig=$(echo "$comboFasta" | cut -f1 -d'.' | sed -e 's/$/_uambig.faa/') && \
    echo "unique headers and removing sequences with ambiguous characters" && \
    python3 /home/rambo/scripts/CrisprCasFinder_flow/python_scripts/fasta_clean.py --input "$comboFasta" --output "$comboFastaUAmbig" --seq_type amino --no_ambigs && \
    if ["$alignprog" == "muscle"]
    then
        echo "running MUSCLE" && \
        muscleOut="${aligndir}/$(basename ${comboFastaUAmbig} | cut -f1 -d'.')_muscle.afa" && \
        /usr/bin/muscle -seqtype auto -in $comboFastaUAmbig -out $muscleOut -maxiters 1000 -quiet && \
        echo "completed MUSCLE for ${i}" && \
        trimalOut="${aligndir}/$(basename ${muscleOut} | cut -f1 -d'.')_trimal.afa" && \
        $trimal -in $muscleOut -out $trimalOut -gappyout -fasta && \
        echo "alignment ${trimalOut} for ${i} trimmed"
    fi

    if ["$alignprog" == "mafft"]
    then
        echo "running MAFFT" && \
        mafftOut="${aligndir}/$(basename ${comboFastaUAmbig} | cut -f1 -d'.')_mafft.afa" && \
        /usr/local/bin/mafft --auto --thread 6 --maxiterate 100 --reorder && \
        echo "completed MAFFT for ${i}" && \
        trimalOut="${aligndir}/$(basename ${mafftOut} | cut -f1 -d'.')_trimal.afa" && \
        $trimal -in $mafftOut -out $trimalOut -gappyout -fasta && \
        echo "alignment ${trimalOut} for ${i} trimmed"
    fi
done

echo "FINISHED"
