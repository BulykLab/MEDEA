import argparse
from argparse import ArgumentParser
from os.path import isfile, isdir, dirname, basename
from time import sleep

def getOneShellOutput(cmd):
	#print cmd
	from subprocess import call, PIPE, Popen
	job_process = Popen(cmd, shell=True, stdout = PIPE, stderr = PIPE)
	out_stream, err_stream = job_process.communicate()
	#if len(err_stream)!=0:
	#    print err_stream
	return [out_stream.strip(),err_stream]

arg_obj = ArgumentParser()
arg_obj.add_argument('dir', metavar = 'dir', help='dir to compress and remove')
args = arg_obj.parse_args()

if not isdir(args.dir):
    raise Exception('Directory must exist.')

if args.dir[-1]!='/':
    args.dir+='/'

directory = dirname(args.dir[:-1])+'/'
prefix = basename(args.dir[:-1])
cmd ="tar -zcvf %s -C %s %s"%(directory+prefix+".tar.gz",directory,prefix)
ret = getOneShellOutput(cmd)
sleep(3)
if len(ret[1])!=0 or not isfile(directory+prefix+".tar.gz"):
    print "ERROR: compressing %s"%(directory+prefix+".tar.gz")
else:
    cmd ="rm -r %s"%(directory+prefix)
    ret = getOneShellOutput(cmd)
    if len(ret[1])!=0:
        print "ERROR: deleting %s"%(directory+prefix)
