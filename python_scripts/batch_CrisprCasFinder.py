#!/usr/bin/python3
import glob
import os
import argparse
import subprocess

'''
Ian Rambo
February 9, 2019
Purpose:
Wrapper script for running multiple batch loops of crisprCasFinder
in parallel via GNU Parallel
'''
#------------------------------------------------------------------------------
def optstring_join(optdict):
    """
    Join a dictionary of command line options into a single string.
    """
    optstring = ' '.join([str(param) + ' ' + str(val) for param, val in optdict.items()])
    return optstring
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
print('CRISPRCasFinder options:\n#=============')
print(ccfinder_opts)
print('\n#=============')
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

outDir = '%s/batch-%d-crisprCasFinder-%s' % (opts.workingDir, opts.jobID, opts.projectName)
if not os.path.isdir(outDir) :
    os.makedirs(outDir)
else :
    pass
os.chdir(outDir)

genomes_to_run = genomePaths[indexes[opts.jobID]:indexes[(opts.jobID + 1)]]
analyzed = 0

for g in genomes_to_run :
    ccFindCmd = 'perl %s -in %s %s'  % (ccfinder_path, g, ccfinder_optstring)
    subprocess.call(ccFindCmd, shell = True)
    analyzed += 1
    print('analysis complete for genome %d of %d, batch %d' % (analyzed, len(genomes_to_run), opts.jobID))
