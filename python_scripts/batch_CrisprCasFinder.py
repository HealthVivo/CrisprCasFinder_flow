#!/usr/bin/python3
import glob
import os
import argparse
import subprocess
import hashlib
import magic
import logging

'''
Ian Rambo
February 9, 2019
Purpose:
Wrapper script for running multiple batch loops of crisprCasFinder
in parallel via GNU Parallel.

Thirteen... that's a mighty unlucky number... for somebody!
'''
#------------------------------------------------------------------------------
def optstring_join(optdict):
    """
    Join a dictionary of command line options into a single string.
    """
    optstring = ' '.join([str(param) + ' ' + str(val) for param, val in optdict.items()])
    return optstring
#------------------------------------------------------------------------------
def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest() if ashexstr else hasher.digest()
#------------------------------------------------------------------------------
def file_as_blockiter(afile, blocksize=65536):
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)
#------------------------------------------------------------------------------
def hash_sum(g, alg):
    valid_algs = ['sha1', 'sha224', 'sha256', 'sha384', 'sha512', 'md5']
    if alg and alg == 'sha1':
        hash = hash_bytestr_iter(file_as_blockiter(open(g, 'rb')), hashlib.sha1())
    if alg and alg == 'sha224':
        hash = hash_bytestr_iter(file_as_blockiter(open(g, 'rb')), hashlib.sha224())
    if alg and alg == 'sha256':
        hash = hash_bytestr_iter(file_as_blockiter(open(g, 'rb')), hashlib.sha256())
    if alg and alg == 'sha384':
        hash = hash_bytestr_iter(file_as_blockiter(open(g, 'rb')), hashlib.sha384())
    if alg and alg == 'sha512':
        hash = hash_bytestr_iter(file_as_blockiter(open(g, 'rb')), hashlib.sha512())
    if alg and alg == 'md5':
        hash = hash_bytestr_iter(file_as_blockiter(open(g, 'rb')), hashlib.md5())
    elif alg and not alg in valid_algs:
        print('choose a valid algorithm from: %s' % ','.join(valid_algs))

    return hash
#------------------------------------------------------------------------------
#Paths to CrisprCasFinder perl script and sofile
ccfinder_path = '/home/rambo/bin/CRISPRCasFinder/CRISPRCasFinder.pl'
ccfinder_sofile = '/home/rambo/bin/CRISPRCasFinder/sel392v2.so'

parser = argparse.ArgumentParser()
parser.add_argument('--nJobs', type=int, dest='nJobs', action='store', nargs=1, help='parallel job number')
parser.add_argument('--jobID', type=int, dest='jobID', action='store', nargs=1, help='job ID number, 0 to n')
parser.add_argument('--ending', type=str, dest='ending', action='store', nargs=1, help='genome file name ending')
parser.add_argument('--genomeDir', type=str, dest='genomeDir', action='store', nargs=1, help='directory containing genome files')
parser.add_argument('--workingDir', type=str, dest='workingDir', action='store', nargs=1, help='working directory')
parser.add_argument('--msfThreads', type=int, dest='msfThreads', action='store', const=1, nargs='?', help='MacSyFinder threads')
parser.add_argument('--projectName', type=str, dest='projectName', action='store', const='', nargs = '?', help='project name for output directories')
parser.add_argument('--hashAlg', type=str, dest='hashAlg', action='store', const='sha256', nargs = '?', help='hash algorithm to use for testing gzip integrity. Choose from: sha1, sha224, sha256, sha384, sha512, md5. Default == sha256')
opts = parser.parse_args()
print(opts.nJobs)
#==============================================================================
#Command line options for CrisprCasFinder
ccfinder_opts = {'-log':'', '-copyCSS':'', '-repeats':'', '-DBcrispr':'',
'-DIRrepeat':'', '-cas':'', '-ccvRep':'', '-vicinity':10000, '-cluster':20000,
'-minDR':16, '-maxDR':72, '-minSP':8, '-maxSP':64, '-cpuM':opts.msfThreads,
'-definition':'SubTyping', '-getSummaryCasfinder':'', '-betterDetectTrunc':'',
'-quiet':'', '-soFile':ccfinder_sofile, '-keep':''}
ccfinder_optstring = optstring_join(ccfinder_opts)
print('CRISPRCasFinder options:\n#=============\n%s\n#=============' % ccfinder_optstring)
#==============================================================================
globString = '%s/*.%s' % (opts.genomeDir, opts.ending)

genomePaths = glob.glob(globString)

perLoop = len(genomePaths) / opts.nJobs
remain = len(genomePaths) % opts.nJobs

indexes = list(range(0, len(genomePaths) + 1, int(len(genomePaths)/opts.nJobs)))

if remain :
    #indexes[-1] += remain - 1
    indexes[-1] += remain
else :
    pass

outDir = os.path.join(opts.workingDir, 'batch-%d-crisprCasFinder-%s' % (opts.jobID, opts.projectName))
if not os.path.isdir(outDir) :
    os.makedirs(outDir)
else :
    pass
os.chdir(outDir)
#==============================================================================
genomes_to_run = genomePaths[indexes[opts.jobID]:indexes[(opts.jobID + 1)]]
analyzed = 0

for g in genomes_to_run :
    #Is file gzip compressed?
    if magic.from_file(g).startswith('gzip compressed data') and g.endswith('.gz'):
        #Get hash for gzipped file
        hash0 = hash_sum(g, opts.hashAlg)

        try:
            gunzip_cmd = 'gunzip %s' % g
            gunzip_proc = subprocess.Popen(gzip_cmd, shell = True)
        except subprocess.CalledProcessError as gunzipexc:
            logging.error("error code", gunzipexc.returncode, gunzipexc.output)
        try:
            #run CrisprCasFinder for gunzipped file
            gunzip_file = os.path.splitext(g)[0]
            logging.info('running CrisprCasFinder for %s' % gunzip_file)
            ccfind_cmd = 'perl %s -in %s %s'  % (ccfinder_path, gunzip_file, ccfinder_optstring)
            subprocess.call(ccfind_cmd, shell = True)
        except subprocess.CalledProcessError as ccfindexc:
            logging.error("error code", ccfindexc.returncode, ccfindexc.output)
        analyzed += 1
        #Re-gzip the file
        try:
            gzip_cmd = 'gzip ' + gunzip_file + ' &'
            gzip_proc = subprocess.Popen(gzip_cmd, shell = True)
        except subprocess.CalledProcessError as gzipexc:
            logging.error("error code", gzipexc.returncode, gzipexc.output)
        #Test the gzip compression
        try:
            logging.info('testing gzip compression')
            gztest_cmd = 'gzip -t %s' % g
            gztest_proc = subprocess.Popen(gztest_cmd, shell = True)
            streamdata = gztest_proc.communicate()[0]
            rc = proc.returncode
            if rc == 0:
                logging.info('gzip compression successful')
        except subprocess.CalledProcessError as gztestexc:
            logging.error("error code", gztestexc.returncode, gztestexc.output)

        #Get hash for re-gzipped file
        hash1 = hash_sum(g, opts.hashAlg)

        #Do the hashes match?
        if hash0 == hash1:
            continue
        else:
            wmessage = 'WARNING: file %s may be damaged. %s hashes do not match for gzipped files' % (g, opts.hashAlg)
            logging.warning(wmessage)

    else:
        try:
            logging.info('running CrisprCasFinder for %s' % g)
            ccfind_cmd = 'perl %s -in %s %s'  % (ccfinder_path, g, ccfinder_optstring)
            subprocess.call(ccfind_cmd, shell = True)
        except subprocess.CalledProcessError as ccfindexc:
            logging.error("error code", ccfindexc.returncode, ccfindexc.output)
        analyzed += 1

    logging.info('analysis complete for genome %d of %d, batch %d' % (analyzed, len(genomes_to_run), opts.jobID))
