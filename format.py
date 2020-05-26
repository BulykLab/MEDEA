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
arg_obj.add_argument('genome', metavar='genome', choices=["hg19","hg38","mm9","mm10","dm3"], help='genome to format')
arg_obj.add_argument('-zip', action='store_true', help='if you downloaded as a zip file and not through git clone, add this flag to download LFS files')
args = arg_obj.parse_args()


db_bed_file = 'data/GENRE/%s/db/%s_DNaseSeq/%sBGpool_multLen150x150.bed.gz'%(args.genome,args.genome,args.genome)
db_db_file = 'data/GENRE/%s/db/%s_DNaseSeq/%sBGpool_multLen150x150.db.gz'%(args.genome,args.genome,args.genome)
genome_fa_file = 'data/GENRE/%s/genome/%s_UnmaskedALL_UCSC.fa.gz'%(args.genome,args.genome)
genome_fai_file = 'data/GENRE/%s/genome/%s_UnmaskedALL_UCSC.fa.fai'%(args.genome,args.genome)
crit_repeats_file = 'data/GENRE/%s/criteria/%s_repeats.bed.gz'%(args.genome,args.genome)
preExTbl = 'data/GENRE/%s/db/%s_DNaseSeq/preExTbl.txt'%(args.genome,args.genome)
exTbl = 'data/GENRE/%s/db/%s_DNaseSeq/exTbl.txt'%(args.genome,args.genome)


if args.zip:
	print "Downloading LFS files"
	toDownload = [db_bed_file, db_db_file,genome_fa_file,genome_fai_file]
	for f in toDownload:
		inFile = 'https://github.com/BulykLab/MEDEA/raw/master/'+f
		outFile = homeDir+f
		
		print "Starting %s"%(inFile)
		
		if isfile(outFile):
			getOneShellOutput("rm %s"%(outFile))
		
		cmd = "wget -O %s %s"%(outFile,inFile)
		ret = getOneShellOutput(cmd)
		if not isfile(outFile):
			raise Exception("wget failed.")
else:
	ori = homeDir+genome_fai_file
	tmp = homeDir+'data/GENRE/%s/genome/temp.fa.fai'%(args.genome)
	getOneShellOutput("cp %s %s"%(ori,tmp))
	getOneShellOutput("mv %s %s"%(tmp, ori))
	if not isfile(ori):
		raise Exception("Genome FASTA index file missing.")


toUnzip = [homeDir+db_bed_file,homeDir+db_db_file,homeDir+genome_fa_file,homeDir+crit_repeats_file]
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

