def getRC(x):
    rev = {'A':'T', 'T':'A', 'C':'G', 'G':'C'}
    comp = ""
    for char in x:
        comp+=rev[char]
    rc = reversed(comp)
    rc=''.join(rc)
    return rc

def isInt(x):
    try:
        int(x)
        float(x)
    except ValueError:
        return False
        
    if float(x)!=int(x):
        return False
    
    return True

def isValidInt(x):
    if isInt(x):
        if int(x)>100 or int(x)<0:
            return False
        return True
    else:
        return False

def isValidBins(x):
    import re
    import math
    arr=[]
    y = x.split(',')
    prevEnd=""
    for z in y:
        rang = re.search('^([\(\[])([0-9]+)\-([0-9]+)([\)\]])$',z)
        if rang is not None:
            a = int(rang.group(2))
            b = int(rang.group(3))
            if a>b or a<0 or b>100:
                return False
            if rang.group(1)=='(':
                a-=0.5
            if rang.group(4)==')':
                b+=0.5
        elif isValidInt(z):
            a=int(z)
            b=int(z)
        else:
            return False
        
        if prevEnd=="":
            prevEnd=b
            if a!=0:
                return False
        else:
            if math.fabs(a-prevEnd)==0.5:
                prevEnd=b
            else:
                return False
    
    if prevEnd!=100:
        return False
    
    return True

def isValidName(x):
    import re
    specWords = ['not','in','is','like','glob','match','regexp','and','or','ID','chr','start','stop','default','length']
    if re.match('^[a-z0-9_]+$',x.lower()) and x.lower() not in specWords:
        return True
    return False

def ckIn(FILE,sort):
    import re
    from os.path import isfile
    
    total=True
    seqPresent=False
    
    criteriaNames = {}
    
    IN = open(FILE,'r')
    for i, line in enumerate(IN):
        tabs = line.strip().split("\t")
        if i==0:
            try:
                cN = tabs.index('criteriaName')
                nB = tabs.index('#bins')
                bT = tabs.index('binType')
                sG = tabs.index('subgroups')
                fL = tabs.index('fileLoc')
            except ValueError:
                print "The first line is assumed to be the header, with the following columns: criteriaName, subgroups, binType, #bins, fileLoc. However, your first line doesn't contain all of these columns, so it is impossible to validate. Please add the appropriate columns and try again."
                raise Exception("Add all 5 columns and try again.")
            continue
        if len(tabs)!=5:
            print "line %s: There are not five tabs in this line. Please fill in the appropriate columns and try again."%(i)
            continue
        
        if not (isValidBins(tabs[bT]) or tabs[bT]=="equal"):
            print "line %s: The bin type should be the keyword equal or a valid range (i.e. only include integers 0-100 and integer ranges - (#-#] with any combination of parentheses and brackets where # is between 0-100, separated by commas)."%(i)
            total=False
        
        if isInt(tabs[nB]):
            if tabs[bT]!="equal" and len(tabs[bT].split(","))!=int(tabs[nB]):
                print "line %s: You have the wrong number of bins for the number of bin types you specified (not 'equal' case)."%(i)
                total=False
            if tabs[bT]=="equal" and 100%int(tabs[nB])!=0:
                print "line %s: %s equal bins are not possible because %s doesn't divide 100 evenly."%(i, tabs[nB],tabs[nB])
                total=False
        else:
            print "line %s: The number of bins should always be an integer."%(i)
            total=False
        
        if tabs[cN]=="seq":
            if seqPresent==True:
                print "Line %s: You can only have one seq line."%(i)
            
            seqPresent=True
            flag=False
            counts = re.sub("\s+","",tabs[sG]).split(',')
            crit = set()
            for nuc in counts:
                if not re.match('^[ACGT]+$',nuc):
                    flag=True
                    break
                else:
                    otro = getRC(nuc)
                    if otro==nuc:
                        crit.add(nuc)
                    else:
                        if nuc<otro:
                            crit.add(nuc+"x"+otro)
                        else:
                            crit.add(otro+"x"+nuc)
            if flag:
                print "line %s: Only ACGT combinations allowed in subgroups."%(i)
                total=False
            else:
                final=list(crit)
                print "line %s: The nucleotide combinations considered will be: %s"%(i,", ".join(final))
                for f in final:
                    if not isValidName(f):
                        print "line %s: Not a valid criteria name."%(i)
                        total=False
                        break
                    if criteriaNames.has_key(f):
                        print "line %s: You can't have duplicate criteriaNames."%(i)
                        total=False
                        break
                    else:
                        if tabs[bT]=="equal":
                            BT=tabs[bT]
                            BV=100/int(tabs[nB])
                        else:
                            BT="list"
                            BV=tabs[bT].split(',')
                        criteriaNames[f]=[BT,BV]
        else:
            if len(tabs[sG])!=0:
                print "line %s: This isn't a seq line, so there shouldn't be any subgroups here."%(i)
                total=False
            incl=True
            if not isValidName(tabs[cN]):
                print "line %s: Not a valid criteria name."%(i)
                incl=False
            if len(tabs[cN])>25:
                print "line %s: Keep criteria names under 25 characters please."%(i)
                incl=False
            if criteriaNames.has_key(tabs[cN]):
                print "line %s: You can't have duplicate criteriaNames."%(i)
                incl=False
            if criteriaNames.has_key(tabs[cN]+'s') or criteriaNames.has_key(tabs[cN]+'e') or ((tabs[cN][-1]=='s' or tabs[cN][-1]=='e') and criteriaNames.has_key(tabs[cN][:-1])):
                print "line %s: You can't have a criterion name that is the same as another criterion name with the exception of an additional 's' or 'e' appended to the end. e.g. exon and (exons or exone)"%(i)
                incl=False
            if incl:
                if tabs[bT]=="equal":
                    BT=tabs[bT]
                    BV=100/int(tabs[nB])
                else:
                    BT="list"
                    BV=tabs[bT].split(',')
                criteriaNames[tabs[cN]]=[BT,BV]
            else:
                total=False
        
        if not isfile(tabs[fL]):
            print "line %s: The file specified is not a file."%(i)
            total=False
        else:
            if sort and tabs[cN]!="seq" and len(getOneShellOutput("sort -c -k1,1 -k2,2n %s"%tabs[fL])[1])!=0:
                print "line %s: For the sake of speed, the criteria BED files must be sorted by chromosome and then by start position (i.e. sort -k1,1 -k2,2n %s). Please sort and try again."%(i,tabs[fL])
                total=False
            if tabs[cN]!="seq" and int(getOneShellOutput("awk 'NF!=3' %s | wc -l"%(tabs[fL]))[0])!=0:
                print "line %s: In order to compare the appropriate columns in the BEDTools output, the criteria BED tools can only have the first three columns of the BED file format: chr, start, stop. Please cut the first three columns (i.e. cut -f1-3 %s), and try again."%(i,tabs[fL])
                total=False
            
    IN.close()
    
    if criteriaNames=={} or criteriaNames.keys()==[]:
        print "This are no criteria within your spec file. Add some and try again."
        total=False
    
    if seqPresent:
        seqPresent=",".join(final)
    else:
        seqPresent="You have not given a seq criteria. NucBed and oligonucleotide counts will not be used."
    
    return [seqPresent, total, criteriaNames]

def GenerateTempFilename(temp_dir = '', base_string = None):
    import time
    import hashlib
    from random import random
    from os.path import isdir, isfile
    from subprocess import call
    
    if temp_dir!="" and not isdir(temp_dir):
        temp_dir=""
    
    if temp_dir!='' and temp_dir[-1]!="/":
        temp_dir=temp_dir+'/'
    
    fileTmp= temp_dir + hashlib.md5(time.ctime() + str(random())).hexdigest()
    while isfile(fileTmp):
        fileTmp= temp_dir + hashlib.md5(time.ctime() + str(random())).hexdigest()
    
    call('touch %s'%fileTmp,shell=True)
    
    return fileTmp

def getOneShellOutput(cmd):
    #print cmd
    from subprocess import call, PIPE, Popen
    job_process = Popen(cmd, shell=True, stdout = PIPE, stderr = PIPE)
    out_stream, err_stream = job_process.communicate()
    #if len(err_stream)!=0:
    #    print err_stream
    return [out_stream.strip(),err_stream]

def roundDownToX(base, x):
    return int(x * (int(float(base))/int(x)))

def getBin(binType, binValue, perc):
    
    if binType=="equal":
        return roundDownToX(perc, binValue)
    if binType=="list":
        for BIN in binValue:
            if '-' in BIN:
                inBound = True
                bounds = BIN[1:-1].split("-")
                a=int(bounds[0])
                b=int(bounds[1])
                if BIN[0]=='(' and not (perc>a):
                    inBound=False
                if BIN[0]=='[' and not (perc>=a):
                    inBound=False
                if BIN[-1]==')' and not (perc<b):
                    inBound=False
                if BIN[-1]==']' and not (perc<=b):
                    inBound=False
                if inBound:
                    return BIN
            else:
                if perc==int(BIN):
                    return BIN
        return "ERROR"

def convertInputToCrit(n):
    import re
    
    if re.match('^[ACGT]+$',n):
        otro = getRC(n)
        if otro==n:
            return n
        else:
            if n<otro:
                return n+"x"+otro
            else:
                return otro+"x"+n
    else:
        return n #it will fail down the line.

def parseNest(nestStr,binFields,binName,cull):
    import re
    
    err = []
    
    toNest = re.sub("\s+","",nestStr).split(":")
    critB = []
    critQ = []
    
    for i,n in enumerate(toNest):
        if '(' in n or ')' in n:
            if i==0 and n[0]=='(' and n[-1]==')':
                for x in n[1:-1].split(','):
                    critB.append(convertInputToCrit(x))
                    
            else:
                err.append('Parentheses indicate independently binned criteria. They must be the first in the nesting scheme.')
        else:
            critQ.append(convertInputToCrit(n))
    
    nestingCriteria = critB+critQ
    quart=False
    names = []
    
    if critB==[]:
        err.append("We are not currently accepting a lack of binned combos in the nesting scheme.")
    
    if [x for x in critB if x in critQ]!=[]:
        err.append("Criteria can't both be binned and nested")
        
    if len(nestingCriteria)!=len(set(nestingCriteria)):
        err.append("Can't have duplicate criteria.")
    
    if len(critB)+len(critQ)==0:
        err.append("At least one criterion is needed.")
    
    if [x for x in nestingCriteria if x not in binFields]!=[]:
        print "Available criteria: %s"%(", ".join(binFields))
        print "Given nesting criteria: %s"%(", ".join(nestingCriteria))
        err.append("Some of given nesting criteria do not match up with the spec file.")
    else:
        name = binName+"_"
        
        name+="".join(sorted([str(binFields.index(y))+"b" for y in critB]))
        
        if len(critQ)!=0:
            quart = True
            name+="_"+"_".join(["q".join(map(str,sorted([binFields.index(x)])))+"q" for x in critQ])
        
        if cull:
            names.append("%s_culled"%name)
        else:
            names.append(name)
        names.append("%s_bins"%name)
        
    return [quart, critB, critQ, names, err]


def getAttr(ID, bed, spec, nucToCt, critB, critQ, attrFile):
    
    from os.path import isfile, basename, dirname
    import re
    import time
    import decimal
    
    if not isfile(bed) or not isfile(spec):
        return "Either bed file or spec file doesn't exist."
        
    if [x for x in critB if x in critQ]!=[]:
        return "A criteria can't both be in critB and critQ because the column names (criteria) will be ambiguous."
        
    subNucB = [x for x in nucToCt if x in critB]
    subNucQ = [x for x in nucToCt if x in critQ]
    subNuc = [x for x in nucToCt if x in critB or x in critQ]
    if not ID:
        outFile=GenerateTempFilename()
        ret = getOneShellOutput("cut -f1,2,3 %s | awk '{print $0\"%sFG\"NR-1}' > %s"%(bed,r"\t",outFile))
        if len(ret[1])!=0:
            return "Error getting attribute file: %s"%(ret[1])
    else:
        outFile=bed
    
    filesToPaste = []
    retFlag = False
    
    IN = open(spec,'r')
    for i,line in enumerate(IN):
        tabs=line.strip().split("\t")
        if i==0:
            cN = tabs.index('criteriaName')
            nB = tabs.index('#bins')
            bT = tabs.index('binType')
            sG = tabs.index('subgroups')
            fL = tabs.index('fileLoc')
            continue
        
        if tabs[cN] in critB+critQ or tabs[cN]=='seq':
            if tabs[cN]=='seq':
                if subNuc==[]:
                    continue
                
                if not isfile(tabs[fL]+".fai"):
                    ret = getOneShellOutput("samtools faidx %s"%tabs[fL])
                    if len(ret[1])==0:
                        print "made fai file for fasta file"
                    else:
                        retFlag=True
                        print "ERROR: samtools didn't create the genome fasta index file correctly. nucBed would fail if run, so nothing was done."
                        continue
                
                colsToCut = ["substr($4,3,length($4))"]
                if 'AxT' in nucToCt:
                    colsToCut.append("$5")
                    ATcol = len(colsToCut)-1
                if 'CxG' in nucToCt:
                    colsToCut.append("$6")
                    GCcol = len(colsToCut)-1
                colsToCut.append("$3-$2")
                colsToCut.append("$14")
                
                tmp = GenerateTempFilename()
                ret = getOneShellOutput("nucBed -fi %s -bed %s -seq | sed '1d' | awk '{print %s }' > %s"%(tabs[fL],outFile,('"'+r"\t"+'"').join(map(str,colsToCut)),tmp))
                
                if len(ret[1])==0:
                    
                    if len(getOneShellOutput("sort -c -k1,1n %s"%tmp)[1])!=0:
                        sortFile = GenerateTempFilename(temp_dir=dirname(bed))
                        getOneShellOutput("mv %s %s"%(tmp,sortFile))
                        getOneShellOutput("sort -k1,1n %s > %s"%(sortFile,tmp))
                        getOneShellOutput("rm %s"%sortFile)
                    
                    if subNucQ!=[]:
                        outSeqReal = GenerateTempFilename()
                        filesToPaste.append(outSeqReal)
                        realOUT=open(outSeqReal,'w')
                        realOUT.write("\t".join([x for x in subNuc if x in subNucQ])+"\n")
                    
                    if subNucB!=[]:
                        outSeqBin = GenerateTempFilename()
                        filesToPaste.append(outSeqBin)
                        binOUT=open(outSeqBin,'w')
                        binOUT.write("\t".join([x for x in subNuc if x in subNucB])+"\n")
                        
                        if tabs[bT]=="equal":
                            BT=tabs[bT]
                            BV=100/int(tabs[nB])
                        else:
                            BT="list"
                            BV=tabs[bT].split(',')
                        
                    
                    nucIN=open(tmp,'r')
                    for i,line in enumerate(nucIN):
                        nucBed=line.strip().split("\t")
                        
                        realVal=[]
                        binVal=[]
                        
                        sz = float(nucBed[-2])
                        for nuc in subNuc:
                            if nuc=='AxT':
                                percentage=decimal.Decimal(nucBed[ATcol])*100
                            elif nuc=='CxG':
                                percentage=decimal.Decimal(nucBed[GCcol])*100
                            else:
                                side = nuc.split("x")
                                if len(side)==2:
                                    percentage = (sum(1 for _ in re.finditer('(?=%s|%s)'%(side[0],side[1]), nucBed[-1]))/(2*(sz-len(side[0])+1)))*100
                                else:
                                    percentage = (sum(1 for _ in re.finditer('(?=%s)'%nuc, nucBed[-1]))/(sz-len(nuc)+1))*100
                            if nuc in subNucQ:
                                realVal.append(percentage)
                            if nuc in subNucB:
                                binVal.append(getBin(BT,BV,percentage))
                        if subNucQ!=[]:
                            realOUT.write("\t".join(map(str,realVal))+"\n")
                        if subNucB!=[]:
                            binOUT.write("\t".join(map(str,binVal))+"\n")
                            
                    if subNucB!=[]:
                        binOUT.close()
                    if subNucQ!=[]:
                        realOUT.close()
                    nucIN.close()
                    getOneShellOutput("rm %s"%tmp)
                else:
                    if isfile(tmp):
                        getOneShellOutput("rm %s"%tmp)
                    retFlag=True
                    print "ERROR: nucBed command failed - nothing was done for seq."
            else:
                outReal = GenerateTempFilename()
                
                ret = getOneShellOutput("intersectBed -a %s -b %s -wao%s| cut -f2,3,4,8 | awk -F\"%s\" '{a[$3]+=(($4/($2-$1))*100);}END{for(i in a)print i\"%s\"a[i];}' | cut -c3- | sort -k1,1n | cut -f2 | awk 'BEGIN{OFS=\"%s\"} {if(NR==1) print \"%s\"; print $0}' > %s"%(outFile, tabs[fL], " -sorted " if ID else " ", r"\t",r"\t",r"\t",tabs[cN],outReal))
                
                if len(ret[1])==0:
                    
                    if tabs[cN] in critB:
                        outBin = GenerateTempFilename()
                        filesToPaste.append(outBin)
                        
                        if tabs[bT]=="equal":
                            BT=tabs[bT]
                            BV=100/int(tabs[nB])
                        else:
                            BT="list"
                            BV=tabs[bT].split(',')
                        
                        binOUT=open(outBin,'w')
                        binOUT.write(tabs[cN]+"\n")
                        intersectIN=open(outReal,'r')
                        for i,line in enumerate(intersectIN):
                            if i==0:
                                continue
                            binOUT.write(str(getBin(BT,BV,decimal.Decimal(line.strip())))+"\n")
                        intersectIN.close()
                        binOUT.close()
                        
                    if tabs[cN] in critQ:
                        filesToPaste.append(outReal)
                    else:
                        getOneShellOutput("rm %s"%outReal)
                else:
                    if isfile(outReal):
                        getOneShellOutput("rm %s"%outReal)
                    retFlag = True
                    print "ERROR: intersectBed command failed - nothing was done for %s."%tabs[cN]
                
    IN.close()
    
    if filesToPaste==[]:
        retFlag=True
        print "ERROR: None of the criteria were found correctly."
    
    if not retFlag:
        numCol=len(critB+critQ)+1
        
        ret = getOneShellOutput('paste %s | awk \'{if (NR==1) print "ID%s"$0; else print NR-2"%s"$0;}\' > %s'%(" ".join(filesToPaste), r"\t",r"\t",attrFile))
        if len(ret[1])!=0:
            retFlag=True
            print "ERROR: "+ret[1]
        
        if isfile(attrFile):
            ret = getOneShellOutput("awk 'NF!=%s' %s | wc -l"%(numCol,attrFile))
            if len(ret[1])!=0:
                retFlag = True
                print "ERROR: "+ret[1]
            if isInt(ret[0]) and int(ret[0])!=0:
                retFlag=True
                print "ERROR: At least one line doesn't have the correct number of fields (i.e. criteria)."
            
    
    for f in filesToPaste:
        if isfile(f):
            getOneShellOutput("rm %s"%f)
    if not ID:
        getOneShellOutput("rm %s"%outFile)
    
    if retFlag:
        return "Error(s) occurred within getAttr"
    else:
        return ""

