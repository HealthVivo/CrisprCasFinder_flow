#!/usr/bin/python3
import glob
import os
import argparse
import subprocess
import hashlib
import magic
from warnings import warn

'''
Ian Rambo
February 9, 2019
Purpose:
Wrapper script for running multiple batch loops of crisprCasFinder
in parallel via GNU Parallel.
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
#Paths to CrisprCasFinder perl script and sofile
ccfinder_path = '/home/rambo/bin/CRISPRCasFinder/CRISPRCasFinder.pl'
ccfinder_sofile = '/home/rambo/bin/CRISPRCasFinder/sel392v2.so'

parser = argparse.ArgumentParser()
parser.add_argument('--nJobs', type=int, dest='nJobs', action='store', nargs=1, help='parallel job number')
parser.add_argument('--jobID', type=int, dest='jobID', action='store', nargs=1, help='job ID number, 0 to n')
parser.add_argument('--ending', type=str, dest='ending', action='store', nargs=1, help='genome file name ending')
parser.add_argument('--genomeDir', type=str, dest='genomeDir', action='store', nargs=1, help='directory containing genome files')
parser.add_argument('--workingDir', type=str, dest='workingDir', action='store', nargs=1, help='working directory')
parser.add_argument('--msfThreads', type=int, dest='msfThreads', action='store', nargs=1, const=1, nargs='?', help='MacSyFinder threads')
parser.add_argument('--projectName', type=str, dest='projectName', action='store', nargs=1, const='', help='project name for output directories')
opts = parser.parse_args()
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
        #Get sha256 hash for gzipped file
        gz0_sha256 = hash_bytestr_iter(file_as_blockiter(open(g, 'rb')), hashlib.sha256())

        try:
            gunzip_cmd = 'gunzip %s' % gunzip_file
            gunzip_proc = subprocess.Popen(gzip_cmd, shell = True)
        except subprocess.CalledProcessError as gunzipexc:
            print("error code", gunzipexc.returncode, gunzipexc.output)

        gunzip_file = os.path.splitext(g)[0]
        print('running CrisprCasFinder for %s' % gunzip_file)
        ccfind_cmd = 'perl %s -in %s %s'  % (ccfinder_path, gunzip_file, ccfinder_optstring)
        subprocess.call(ccfind_cmd, shell = True)
        analyzed += 1
        #Re-gzip the file
        try:
            gzip_cmd = 'gzip ' + gunzip_file + ' &'
            gzip_proc = subprocess.Popen(gzip_cmd, shell = True)
        except subprocess.CalledProcessError as gzipexc:
            print("error code", gzipexc.returncode, gzipexc.output)
        #Test the gzip compression
        try:
            print('testing gzip compression')
            gztest_cmd = 'gzip -t %s' % g
            gztest_proc = subprocess.Popen(gztest_cmd, shell = True)
            streamdata = gztest_proc.communicate()[0]
            rc = proc.returncode
            if rc == 0:
                print('gzip compression successful')
        except subprocess.CalledProcessError as gztestexc:
            print("error code", gztestexc.returncode, gztestexc.output)

        #Get sha256 hash for re-gzipped file
        gz1_sha256 = hash_bytestr_iter(file_as_blockiter(open(g, 'rb')), hashlib.sha256())

        #Do the hashes match?
        if gz0_sha256 == gz1_sha256:
            continue
        else:
            warn('sha256 hashes do not match for %s' % g)

    else:
        ccfind_cmd = 'perl %s -in %s %s'  % (ccfinder_path, g, ccfinder_optstring)
        subprocess.call(ccfind_cmd, shell = True)
        analyzed += 1

    print('analysis complete for genome %d of %d, batch %d' % (analyzed, len(genomes_to_run), opts.jobID))
