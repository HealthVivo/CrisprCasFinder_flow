#!/usr/bin/env python3

import argparse
import re
import logging

parser = argparse.ArgumentParser()
parser.add_argument('--tree', type=str, dest='tree', action='store',
nargs = 1, help='input tree. Required.')
parser.add_argument('--taxonomy', type=str, dest='taxonomy', action='store',
nargs = 1, help='taxonomy table. Required.')
parser.add_argument('--out_tree', type=str, dest='out_tree', action='store',
nargs = 1, help='output tree. Required.')

opts = parser.parse_args()
tax_dict = {}

with open(opts.taxonomy[0], 'r') as taxonomy:
    for tax in taxonomy:
        tax.replace('"', '')
        tax_list = tax.split(',')
        if len(tax_list == 3):
            species = tax_list[0]
            taxid = tax_list[1]
            tax_full = '%s;%s' % (taxid, species)
            accession = tax_list[2]
            if ';' in accession:
                accession_list = accession.split(';')
                for acc in accession_list:
                    a = re.findall(r'\/(.*?\.\d+)$', acc)
                    tax_dict[a] = tax_full
            else:
                a = re.findall(r'\/(.*?\.\d+)$', accession)[0]
                tax_dict[a] = tax_full
        elif len(tax_list == 2):
            if ';' ih tax_list[1]:
                pass
            else:




with open(opts.tree[0], 'r') as tree:
    pass
