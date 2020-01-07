import getgra
import sys
import datetime
from optparse import OptionParser
import os




program_name = sys.argv[0]
baseversion = "0"
subversion = "13"
version = baseversion +  "." + subversion
exactlynow = datetime.datetime.now()
now = exactlynow.replace(microsecond=0).isoformat()

validexts = [".xml"]





def dotestgra(testgrain, logfile):
    filenames = []
    for root, dirs, thefiles in os.walk(testgrain):
        for filename in thefiles:
            fullname = os.path.join(root, filename)
            (base, ext) = os.path.splitext(filename)
            if ext in validexts:
                filenames.append(fullname)
    outfile = open(testgraoutfilename, 'w', encoding='utf8')
    for filename in filenames:
        print(filename, file=outfile)
        (sentence, grastr) = getgra.getgra(filename, logfile, utterance=True)
        print(sentence, file=outfile)
        print(grastr, file=outfile)
    outfile.close()

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="test on  this file only")
parser.add_option("-i", "--inpath",
                   dest="inpath", default="testgrain",
                  help="path to input files")
parser.add_option("-o", "--outpath",
                   dest="outpath", default="testgraout",
                  help="path to output files")
parser.add_option("-l", "--logpath",
                   dest="logpath", default="testgralog",
                  help="path to log files")
parser.add_option("--logfile", dest="logfilename", default="testgralog.txt",
                  help="log filename")
parser.add_option("--outfile", dest="outfilename", default="testgraout.txt",
                  help="output filename")

(options, args) = parser.parse_args()

testgrain = options.inpath
testgraout = options.outpath
testgralog = options.logpath
testgraoutfilename = os.path.join(testgraout, options.outfilename)
testgralogfilename = os.path.join(testgralog, options.logfilename)

if options.filename is not None:
    mygrafile = options.filename
else:
    mygrafile = ""

if mygrafile!="":
    testgralogfile = open(testgralogfilename, 'w', encoding='utf8')
    result= getgra.getgra(mygrafile,testgralogfile)
    print(result)
else:
    testgralogfile = open(testgralogfilename, 'w', encoding='utf8')
    dotestgra(testgrain, testgralogfile)
    exit()