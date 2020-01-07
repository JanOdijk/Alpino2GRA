# Alpino2GRA
Converts Alpino syntactic structures into CHILDES GRA tier representations

Alpino2GRA
The python modules getgra.py, testgra.py and dependencies.py are intended for generating  CHAT %GRA tiers from Alpino syntactic structures.

The python module getgra.py contains a function getgra():

def getgra(afile, logfile, skipboring=True, utterance=False):

-afile is the Alpino xml filenaam for an utterance
-logfile is the file to log to.

The keyword parameters skipboring and utterance are not relevant and must be kept at their default values.

The output is a tuple (sentence,GRAtier), in which:
 
-sentence is a string with numbered tokens, e.g. 

1:wie 2:zit 3:er 4:op 5:de 6:fiets 7:?

This is only useful for testing purposes and can be ignored otherwise.

-GRAtier is a string containing the CHAT GRA tier, e.g. 

%GRA:  1|2|su 2|0|ROOT 3|2|mod 4|2|ld 5|6|det 6|4|obj1 7|0|PUNCT 

The module testgra can be used to test getgra. It takes files from an input folder  (default: testgrain), writes the results to an output folder
(default: testgraout) and writes a logfile (default: testgralog.txt) to a log folder (default: testgralog).

The folder testgrain contains a whole range of testfiles (9.926) in multiple folders.

The result of testgra consist of 1 file (defaultnaam: testgraout.txt) with 3 lines per input file: filenaam, sentence, GRAtier, e,g.:
 
testgrain\Erlinde\IAA_Erlinde\VanKampen_sarah09_u00000000271.xml
1:wie 2:zit 3:er 4:op 5:de 6:fiets 7:?
%GRA:  1|2|su 2|0|ROOT 3|2|mod 4|2|ld 5|6|det 6|4|obj1 7|0|PUNCT 

 
The folder testgraref contains a reference outputfile and a reference  logfile. Note: the testset contains ill-formed syntactic structures, so the logfile contains messages. 

Calling testgra using default settings is done as follows:

python testgra.py

The parameter -h gives an overview of the parameters:

Usage: testgra.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILENAME, --file=FILENAME
                        test on  this file only
  -i INPATH, --inpath=INPATH
                        path to input files
  -o OUTPATH, --outpath=OUTPATH
                        path to output files
  -l LOGPATH, --logpath=LOGPATH
                        path to log files
  --logfile=LOGFILENAME
                        log filename
  --outfile=OUTFILENAME
                        output filename


The module getgra.py imports the module dependencies.py, which contains only constants ad functions.

Jan Odijk
2018-08-16

