#!/usr/bin/python3

import argparse
import re
import logging
from Bio import SeqIO
"""
Remove illegal characters from FASTA headers and add a label
to make headers unique.
The user can opt to remove sequences with ambiguous characters that may not work
 with certain MSA and alignment trimming software.
The user can opt to remove identical sequences.
"""
parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, dest='input_file', action='store',
nargs = 1, help='input FASTA. Required.')
parser.add_argument('--output', type=str, dest='output_file', action='store',
nargs = 1, help='output FASTA. Required.')
parser.add_argument('--seq_type', action = 'store', dest = 'seqtype',
nargs = 1, help='sequence type, specify "nuc" or "amino". Required.')
parser.add_argument('--no_ambigs', default=False, action='store_const', dest = 'ambig',
const=True, help='remove sequences with ambiguous characters')
parser.add_argument('--uniq_seqs', default=False, action = 'store_const', dest = 'uniq',
const=True, help = 'remove duplicate sequences')

opts = parser.parse_args()

illegals = re.compile(r'\:|\,|\)|\(|\;|\,|\]|\[|\,|\'')
header_counts = {}

#Valid and ambiguous amino acids
valid_aa = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']
ambig_aa = ['B','J','O','U','X','Z']
#Ambiguous nucleotides
ambig_nuc = ['R','Y','W','S','K','M','D','V','H','B']
#Load the FASTA sequence data
#seq_dict = SeqIO.to_dict(SeqIO.parse(opts.input_file[0], 'fasta'))
seq_recs = SeqIO.parse(opts.input_file[0], 'fasta')
seq_recs_uhead = []
for record in seq_recs:
    if str(record.seq).endswith('*'):
        record.seq = record.seq[:-1]
    id_legal = illegals.sub('_', record.id)
    if record.id in header_counts:
        header_counts[record.id] += 1
        nrecord = record
        nrecord.id = id_legal + '_copy%d' % header_counts[record.id]
        nrecord.description = ''
        seq_recs_uhead.append(nrecord)
    else:
        header_counts[record.id] = 0
        seq_recs_uhead.append(record)


#seq_dict = SeqIO.to_dict([seq_recs_uhead)
seq_dict = SeqIO.to_dict([s for s in seq_recs_uhead if not 'copy' in s.id])

#If no_ambigs == True, remove sequences with ambiguous amino acids or nucleotides
if opts.ambig and opts.seqtype[0] == 'amino':
    #seq_objs = [seq_dict[a] if seq_dict[a] and all([not c in str(seq_dict[a].seq]).upper() for a in seq_dict.keys() for c in ambig_aa])]
    seq_objs = [seq_dict[a] for a in seq_dict.keys() if seq_dict[a] and all([not c in str(seq_dict[a].seq).upper() for c in ambig_aa])]
elif opts.ambig and opts.seqtype[0] == 'nuc':
    seq_objs = [seq_dict[a] for a in seq_dict.keys() if seq_dict[a] and all([not c in str(seq_dict[a].seq).upper() for c in ambig_nuc])]
else:
    seq_objs = [seq_dict[a] for a in seq_dict.keys() if seq_dict[a]]

# seq_objs_out = []
# for s in seq_objs:
#     id_legal = illegals.sub('_', s.id)
#     if s.id in header_counts:
#         header_counts[s.id] += 1
#         sn = s
#         sn.id = id_legal + '_%d' % header_counts[s.id]
#         seq_objs_out.append(sn)
#     else:
#         header_counts[s.id] = 0
#         seq_objs_out.append(s)
#print(seq_objs_out)
#if seq_objs_out:
if seq_objs:
    #print('%d total sequences, removed %d sequences with ambiguous characters, %d remain' % (len(seq_dict.keys()), (len(seq_dict.keys()) - len(seq_objs_out)), len(seq_objs_out)))
    print('%d total sequences, removed %d sequences with ambiguous characters, %d remain' % (len(seq_dict.keys()), (len(seq_dict.keys()) - len(seq_objs)), len(seq_objs)))
    with open(opts.output_file[0], 'w') as out_handle:
        #print('writing %d sequences to file %s' % (len(seq_objs_out), opts.output_file[0]))
        print('writing %d sequences to file %s' % (len(seq_objs), opts.output_file[0]))
        #SeqIO.write(seq_objs_out, out_handle, 'fasta')
        SeqIO.write(seq_objs, out_handle, 'fasta')


else:
    logging.warning('WARNING: no sequence objects to write! Exiting...')
    quit()



# with open(opts.input_file, 'r') as inseqs, open(opts.output_file, 'w') as outseqs:
#     for f in inseqs:
#         f = f.rstrip()
#         if f.startswith('>'):
#             f_legal = illegals.sub('_', f)
#             if f in header_counts:
#                 header_counts[f] += 1
#                 outseqs.write('%s_%d\n' % (f_legal, header_counts[f]))
#             else:
#                 header_counts[f] = 0
#                 outseqs.write('%s\n' % f_legal)
#         else:
#             outseqs.write('%s\n' % f)
