#!/usr/bin/env python3
"""
2019 Ian Rambo
Fetch FASTA sequences from Prodigal output based on CrisprCasFinder gff3 report.

Specify an output data frame for TARGET. This will contain the
query name and respective output FASTA file containing the target sequences.
"""
import argparse
from warnings import warn
import pandas as pd
from Bio import SeqIO
import re
import os

parser = argparse.ArgumentParser()
parser.add_argument('--cas_gff', dest='cas_gff', type = str, nargs=1,
action='store', help='cas report gff file')
parser.add_argument('--prodigal_file', dest = 'prodigal', type = str, nargs = 1,
action = 'store', help='path to prodigal fasta output file')
parser.add_argument('--working_dir', dest = 'workdir', type = str, nargs = 1,
action = 'store', help='working directory')
parser.add_argument('--project_name', dest = 'project_name', type = str, nargs = 1,
action = 'store', help='project name for output files')

args = vars(parser.parse_args())

if not os.path.exists(args['workdir'][0]):
    os.mkdir(args['workdir'][0])
else:
    pass
#------------------------------------------------------------------------------
print('BEGIN')
crdf = pd.read_csv(args['cas_gff'][0], comment = '#', header = None,
names = ['seqid', 'source', 'ftype', 'targetid', 'phase',
'start', 'end', 'strand', 'attributes'], sep = '\s+')

cas_ids = list(set(crdf['source'].tolist()))
seq_dict = SeqIO.to_dict(SeqIO.parse(args['prodigal'][0], 'fasta'))

for cas in cas_ids:
    print('processing %s...' % cas)
    sfile = os.path.join(args['workdir'][0], '%s_%s_prodigalSeqs.faa' % (cas, args['project_name'][0]))
    nseqs = 0
    with open(sfile, 'w') as sf:
        subset = crdf[crdf['source'] == cas]
        seqids = list(set(subset['seqid'].tolist()))
        seqobjs = [seq_dict[x] if x in seq_dict else print('result id %s not in seq_dict' % x) for x in seqids]
        seqobjs = [x for x in seqobjs if x]
        if seqobjs:
            SeqIO.write(seqobjs, sf, 'fasta')
            nseqs += len(seqobjs)
            print('%d sequences for %s written to %s' % (nseqs, cas, sfile))
        else:
            message = 'No sequence objects found for %s' % cas
            warn(message)
#==============================================================================
print('FINISHED')

quit()
