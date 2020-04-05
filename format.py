from os.path import isfile, dirname, realpath
from argparse import ArgumentParser

def getOneShellOutput(cmd):
	#print cmd
	from subprocess import call, PIPE, Popen
	job_process = Popen(cmd, shell=True, stdout = PIPE, stderr = PIPE)
	out_stream, err_stream = job_process.communicate()
	#if len(err_stream)!=0:
	#    print err_stream
	return [out_stream.strip(),err_stream]

homeDir = dirname(realpath(__file__))+"/"


arg_obj = ArgumentParser()
arg_obj.add_argument('-zip', action='store_true', help='if you downloaded as a zip file and not through git clone, add this flag to download LFS files')
args = arg_obj.parse_args()


if args.zip:
	toDownload = ['data/GENRE/hg19/db/hg19_DNaseSeq/hg19BGpool_multLen150x150.bed.gz', 'data/GENRE/hg19/db/hg19_DNaseSeq/hg19BGpool_multLen150x150.db.gz','data/GENRE/hg19/genome/hg19_UnmaskedALL_UCSC.fa.gz','data/GENRE/hg19/genome/hg19_UnmaskedALL_UCSC.fa.fai']
	for f in toDownload:
		inFile = 'https://github.com/BulykLab/MEDEA/raw/master/'+f
		outFile = homeDir+f
		
		if isfile(outFile):
			getOneShellOutput("rm %s"%(outFile))
		
		cmd = "wget -O %s %s"%(outFile,inFile)
		ret = getOneShellOutput(cmd)
		if not isfile(outFile):
			raise Exception("wget failed.")


toUnzip = [homeDir+"data/GENRE/hg19/db/hg19_DNaseSeq/hg19BGpool_multLen150x150.bed.gz",homeDir+"data/GENRE/hg19/db/hg19_DNaseSeq/hg19BGpool_multLen150x150.db.gz",homeDir+"data/GENRE/hg19/genome/hg19_UnmaskedALL_UCSC.fa.gz",homeDir+"data/GENRE/hg19/criteria/hg19_repeats.bed.gz"]
print "gunzipping files"
for f in toUnzip:
	print "Starting %s"%(f)
	if not isfile(f):
		raise Exception("File doesn't exist.")
	
	cmd = "gunzip %s"%(f)
	ret = getOneShellOutput(cmd)
	if not isfile(f.rsplit('.',1)[0]) or len(ret[1])!=0:
		raise Exception("gunzip failed.")


print "Formatting GENRE DB"
preExTbl = homeDir+"data/GENRE/hg19/db/hg19_DNaseSeq/preExTbl.txt"
exTbl = homeDir+"data/GENRE/hg19/db/hg19_DNaseSeq/exTbl.txt"

if not isfile(preExTbl):
	raise Exception("Initial formatting file doesn't exist.")

cmd = "awk 'BEGIN{OFS=FS=\"%s\"} {if(NR!=1) {$5=\"%s\"$5}; print $0}' %s > %s"%(r"\t",homeDir,preExTbl,exTbl)
ret = getOneShellOutput(cmd)
if not isfile(exTbl) or len(ret[1])!=0:
	raise Exception("Formatting failed.")

cmd = "rm %s"%(preExTbl)
ret = getOneShellOutput(cmd)
if isfile(preExTbl) or len(ret[1])!=0:
	raise Exception("Pre-formatting file not fully removed.")

print "GENRE successfully formatted."

