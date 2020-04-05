# MEDEA

MEDEA identifies lineage-specifying transcription factors (TFs) from chromatin accessibility assays by:
1. Identifying cell-type-specific open regions through pairwise comparisons with a highly curated reference set (MEDEA)
2. Making matched background sets for the motif enrichment analysis (GENRE)
3. Performing TF motif enrichment analysis with an AUROC metric (Glossary)


## Getting Started

### Dependencies
```
wget (tested in GNU wget 1.12, 1.15, 1.17.1)
awk (tested in GNU awk 3.1.7, mawk 1.3.3, awk version 20070501)
sed (tested in GNU sed 4.2.1 & 4.2.2, OSX sed compile.c v 1.28)
Python 2.X (tested in 2.6.6 and 2.7.6)
    argparse
    os
    sqlite3
    re
    time
    random
    csv
    math
    hashlib
    subprocess
    decimal
    itertools
R (tested in 3.0.2 and 3.2.3)
    zoo
    Biostrings
    methods
    BiocGenerics
    parallel
    IRanges
    XVector
BEDTools (tested in 2.23.0, 2.25.0, and 2.26.0)
sqlite3 (tested in 3.6.20 and 3.11.0)
```

Verify all dependencies installed. These dependencies are also for Glossary-GENRE.
```
$ bash envTest_MEDEA.sh
```

### Installing

Format MEDEA and gunzip files. If you have downloaded the zip file directly from the website, this script will also download the large files from LFS.

```
$ python format.py
```

Optional Arguments:
```
-zip: if you downloaded as a zip file and not through git clone, add this flag to download LFS files
```

## How to Run

### MEDEA Inputs

Obtain a foreground set.
1. Must be in BED file format.
2. The first three columns will be utilized. A scoring column may also be used with the -best flag to only take the best X peaks from that column (see below for more information).
3. For this release, the foreground must be aligned to the hg19 genome and be 150 bp.
4. A test set for MEDEA is given in testing/DNASE.K562.merged.bed. (More info below)

IDs within this release:
```
Genomes (genome_ID): hg19
Databases (db_ID): hg19_DNaseSeq - this GENRE database covers the human hg19 genome tiled to 150 bp.
Motifs (motifs_ID): 
	benchmark-kmer - 13 kmer modules with develepmental TFs selected in this study (see Fig. 1-2,6)
	benchmark-pwm - 13 pwms with develepmental TFs selected in this study (see Fig. S1B,D)
	lymphoid-pwm - PWMs relevant to the hematopoietic lineage selected in this study (see Fig. S10)
	glossary-kmer - 108 glossary kmer modules from (Mariani et al., 2017) (see Fig. 4-5)
	explorative-pwm - 99 PWMs selected to cover the human TF specificity landscape (see Fig. 4-5)
MEDEA reference sets (ref_ID): hg19_ENCODE-DREAM_DNase_relaxed
```


### MEDEA
```
$ bin/MEDEA/MEDEA "db_ID" "FG set" "motifs_ID" "ref_ID"
```

Required Arguments:
```
db_ID: see above
FG set: your foreground set in BED format
motifs_ID: see above
ref_ID: see above
```

Optional Arguments:
```
-seed seed : seed for randomization, preferably a number (anything given is converted to a string);
             default 123456789
-outDir outDir : output directory name.
                 All pairwise subtractions, backgrounds, and Glossary output files will be sorted here.
                 If not given, the output directory prefix will be the same as the FG file;
                 suffix will be ref_ID
-best #,asc/desc,# : comma-delimited list of column number to sort on,
                     ascending(asc)/descending(desc) sorting method, number of regions,
                     i.e. 4,desc,500 to sort descending on column 4 and take the best 500 peaks
-skip delim,# : skip if cell line is the same;
                comma-delimited list to parse filename for cell line: delimiter, index of 0-based split array
                i.e. .,1
-compress: if given, compress the matches directory outputted by the Glossary.
```

#### Output

1. Best peaks (BED and FASTA) of FG set (or a copy of the FG set if -best flag not given)
2. All pairwise subtractions (BED and FASTA) between FG set and ENCODE-DREAM reference set (best peaks if -best flag else all peaks)
3. GENRE Backgrounds (BED and FASTA) for FG set and pairwise subtractions
4. Matches directory for FG_set and pairwise subtractions. (Not relevant for analyses here; usually compressed into tar.gz file.)
    1. Best Matches file
    2. Foreground motif stats file
    3. Foreground distance from center file
    4. Background motif stats file
    5. Background distance from center file
5. Glossary output files with AUROC statistics for FG_set and pairwise subtractions
    1. Motif: Motif filename
    2. AUROC: enrichment of motif in foreground over background
    3. p-val: Wilcoxon p-value of AUROC - significance of enrichment
    4. numFG: number of peaks with motif match in foreground
    5. numBG: number of peaks with motif match in background
    6. medFG: median distance of best motif match from peak center in foreground
    7. medBG: median distance of best motif match from peak center in background
    8. posTest: position Wilcoxon test p-value
    9. motifScore: optimal score for discriminative motif matching between foreground and background peaks
    10. \*MEDEAthresh: AUROC that distinguishes good and bad motifs
    11. \*overThresh: yes if the motif's AUROC passes its MEDEA threshold; no otherwise
6. MEDEA AUROC file for each FG_set over all pairwise subtractions (median AUROC values)

\*NOTE:
These columns are only displayed with the motif IDs glossary-kmer and explorative-pwm. For those, we have also calculated MEDEA thresholds that capitalize on a large set of 610 DNase-seq datasets to provide a discriminative AUROC score that distinguishes a good score (see Fig. S4C and Extended Methods).


### Add MEDEA reference set
```
$ bin/MEDEA/addRefSet "genome_ID" "refDir"
```

Required Argumets:
```
genome_ID: see above
refDir: directory of reference set BED files - the name of this directory will be the reference set ID suffix
```

#### Output

1. Message with MEDEA reference set ID


### Running GENRE
```
$ bin/GENRE/GENRE "db_ID" "FG set"
```

Required Arguments:
```
db_ID: see above
FG set: your foreground set in BED format
```
Optional Arguments:
```
-seed seed: seed for randomization, preferably a number (anything given is converted to a string);
            default 123456789
-BG BG: Background output directory name. If not given, prefix will be the same as the FG file;
        suffix will be the db_ID
-mult mult: multiplicity factor (positive integer); default 1 (mult 1 is needed to run with the Glossary)
```


#### Output 

1. Message with seed and BG filename.
2. Copy of Foreground BED file
3. Foreground FASTA file
4. Background BED and FASTA file


### Running Glossary
```
$ bin/glossary/glossary "FG FASTA file" "BG FASTA file" "motifs_ID"
```

Required Arguments:
```
FG FASTA file: your foreground set in FASTA file format
BG FASTA file: the background set in FASTA file format
motifs_ID: see above
```
NOTE: Both the FASTA files are outputted by GENRE if you don't have them from other sources.


#### Output

1. Matches directory
    1. Best Matches file
    2. Foreground motif stats file
    3. Foreground distance from center file
    4. Background motif stats file
    5. Background distance from center file
2. Glossary output files with AUROC statistics for FG_set and pairwise subtractions
    1. Motif: Motif filename
    2. AUROC: enrichment of motif in foreground over background
    3. p-val: Wilcoxon p-value of AUROC - significance of enrichment
    4. numFG: number of peaks with motif match in foreground
    5. numBG: number of peaks with motif match in background
    6. medFG: median distance of best motif match from peak center in foreground
    7. medBG: median distance of best motif match from peak center in background
    8. posTest: position Wilcoxon test p-value
    9. motifScore: optimal score for discriminative motif matching between foreground and background peaks


### Running Glossary-GENRE
```
$ bin/glossary/glossary_GENRE "db_ID" "FG set" "motifs_ID"
```

Required Arguments:
```
db_ID: see above
FG set: your foreground set in BED format
motifs_ID: see above
```

Optional Arguments:
```
-seed seed: seed for randomization, preferably a number (anything given is converted to a string);
            default 123456789
-BG BG: Background output directory name. If not given, prefix will be the same as the FG file;
        suffix will be the db_ID
```


#### Output

1. Same output is given as for GENRE and Glossary separately.


### Add your own motif sets
```
$ bin/glossary/addMotifSet "motifs" "type"
```

Required Arguments:
```
motifs: file of motifs separated by >motif_name or directory of single motif files with the
        motif_name being the filename (minus extension)
type: type of motif; either pwm or kmer
```

Motif file specifications:
1. pwm
    1. rectangular matrix
    2. all positions add to 1
    3. bases are assumed to be ACGT
    4. bases must be labeled if length is 4 or 5bp, though it's always a good idea to label them
    5. positions may or may not be labeled
    6. single file option must be have bases on the rows
2. kmer
    1. two columns separated by non-newline whitespace: kmer and E-score


## Demo for installation verification

### Testing MEDEA

For the given example with K562 DNase-seq peaks:
```
$ bin/MEDEA/MEDEA hg19_DNaseSeq testing/DNASE.K562.merged.bed benchmark-kmer \
hg19_ENCODE-DREAM_DNase_relaxed -best 4,desc,500 -skip .,1 -compress
```
Output should be the same as that in
```
testing/originalOutput/DNASE.K562.merged_ref_hg19_ENCODE-DREAM_DNase_relaxed/
```

### Testing GENRE
For the given example with the best 500 peaks of K562 DNase-seq:
```
$ bin/GENRE/GENRE hg19_DNaseSeq testing/DNase_K562_best500.bed -BG testing/DNase_K562_best500_hg19BG
```
Output should be the same as that in
```
testing/originalOutput/DNase_K562_best500_hg19BG/
```

### Testing Glossary
For the above example,
```
$ bin/glossary/glossary testing/DNase_K562_best500_hg19BG/DNase_K562_best500.fa \
testing/DNase_K562_best500_hg19BG/DNase_K562_best500_hg19BG.fa benchmark-kmer
```
Output should be the same as that in
```
testing/originalOutput/DNase_K562_best500_hg19BG/
```

### Testing Glossary-GENRE
Remaking the example above in one command:
```
$ bin/glossary/glossary_GENRE hg19_DNaseSeq testing/DNase_K562_best500.bed benchmark-kmer
```
Output should be the same as that in
```
testing/originalOutput/DNase_K562_best500_hg19-DNaseSeqBG/
```


## Acknowledgements
We thank Anshul Kundaje (Stanford University), the ENCODE-DREAM Challenge Organizers, and the following ENCODE data production centers (Snyder lab, Myers lab, Stamatoyannopoulos lab) for the production of the ENCODE-DREAM DNase-seq datasets that we use as our reference sets. These datasets where originally downloaded from: https://www.synapse.org/#!Synapse:syn6176236
