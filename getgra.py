import dependencies


#program_name = sys.argv[0]
baseversion = "0"
subversion = "13"
version = baseversion + "." + subversion

rootrel = 'ROOT'
puncrel = 'PUNCT'
unknownpostag = 'NA()'
underscore = "_"
possep = "-"
space= " "
grasep= "|"
puncposset = ['let()']

excludeposcats = ["TSW()", "LET()"]
boringrelations = ['--/--']
graprefix = "%GRA:  "

caheads={'hd':1, 'cmp':2, 'crd':3, 'dlink':4, 'body':5, 'rhd':6 , 'whd':7, 'nucl':8}
rootheads={'hd':1, 'cmp':2, 'crd':3, 'dlink':4, 'body':5, 'nucl':6, 'dp':7}
heads = caheads
rootposcats = ["TSW()", "LET()"]

dpset = ['dp']  # relations for discourse fragments
duset = ['du'] # categories for discourse units



def addroottuples(filename, logfile, tuples):
    hererootrels=[]
    for el in tuples:
        (dw,dp,rel,hw,hp)= tuples[el]
        if rel in boringrelations:
            hererootrels.append((el, tuples[el]))
    for (el,tel) in hererootrels:
        (db, de, hb, he) = el
        (dw, dp, rel, hw, hp) = tel
        if dp.lower() in puncposset:
            therel = puncrel
        else:
            therel = rootrel
        tuples[(db,de, '-1', '0')] = (dw, dp, therel, '', '')
        if hp.lower() in puncposset:
            tuples[(hb,he, '-1', '0')] = (hw, hp, puncrel, '', '')
        # tuples[(hb,he, '-1', '0')] = (hw, hp, rootrel, '', '')


def dpfound(node):
    result = False
    for child in node:
        if not result:
            result = isadp(child)
    return result



def gettokenpositions(tlist):
    resultlist =[]
    for el in tlist:
        postup = el[0]
        (b,e) = postup
        for val in range(b,e+1):
            resultlist.append(val)
    return(resultlist)

def getyield(tuples):
    wordset = set()
    for el in tuples:
        (db,de,hb,he) = el
        (dw,dp,rel,hw,hp) = tuples[el]
        if de != '0': wordset.add(((int(db)+1, int(de)), dw))
        if he != '0': wordset.add(((int(hb)+1,int(he)), hw))
    wordlist= list(wordset)
    sortedwordlist = sorted(wordlist,key=lambda x: x[0])
    return sortedwordlist


def getgra(afile, logfile, skipboring=True, utterance=False):
    #format: (d|h|rel)+
    heads = rootheads
    themode = 'triples'
    strict = True
    tuples = {}
    sentence = dependencies.getTuples(afile, logfile, themode, tuples, strict, utterance=True)

    #add tuples for boring relations ROOT
    addroottuples(afile, logfile, tuples)



    gralist = []
    for el in tuples:
        dependency = tuple2gradep(el,tuples)
        gralist.append(dependency)

    #filter for boringrelations
    if skipboring:
        filteredgralist = [(d,h,rel) for (d,h,rel) in gralist if rel not in boringrelations]
    else:
        filteredgralist = gralist
    #warn for rootless and multiple root utterances
        rootlist = [(d,h,rel) for (d,h,rel) in filteredgralist if rel != rootrel]

        lrootlist = len(rootlist)
        if lrootlist == 0:
            print('No ROOT found in {}'.format(afile), file=logfile)
        if lrootlist > 1:
            print('Multiple ROOTs found in {}'.format(afile), file=logfile)

    #sort the filteredlist
    sortedgralist = sorted(filteredgralist, key=lambda t: getkey(t))
    result = gralist2str(sortedgralist)

    tlist = getyield(tuples)
    wlist = tuplelist2list(tlist)
    tuplesent = space.join(wlist)

    #check whether all tokens are covered
    #check which ones are covered by mwus
    tokposlist = gettokenpositions(tlist)
    sentlist = sentence.split()
    sentlistlen = len(sentlist)
    senttoklist = range(1,sentlistlen+1)
    if tokposlist != senttoklist:
        for el in senttoklist:
            if el not in tokposlist:
                print('Problem: Token {} not covered in {}'.format(str(el), afile), file=logfile)

#old and not correet does nt take into account mwus
#    sentlen = len(sentence.split())
#    coveredtokens = {int(d) for (d,h,rel) in sortedgralist}.union({int(h) for (d,h,rel) in sortedgralist})
#    for i in range(sentlen):
#        if (i+1) not in coveredtokens:
#            print('Token {} not covered in {}'.format(str(i+1), afile), file=testgralogfile)

    return(tuplesent, result)

def tuple2gradep(el,tuples):
    (db,de,hb,he)=el
    (dw,dp,rel,hw,hp)= tuples[el]
    dep = getloc(db,de)
    hd = getloc(hb,he)
    return(dep,hd,rel)

def tuplelist2list(tlist):
    outlist = []
    for el in tlist:
        ((b,e),w) = el
        modwlist= w.split()
        modw = underscore.join(modwlist)
        if e==b:
            thestr = str(e) + ':' + modw
        else:
            thestr = str(b)+possep+str(e) + ':' + modw
        outlist.append(thestr)
    return outlist

def getkey(triple):
    (d,h,l) = triple
    dh = d.find(possep)
    hh = h.find(possep)
    if dh!= -1:
        dp = d[:dh]
    else:
        dp = d
    if hh!= -1:
        hp = h[:hh]
    else:
        hp = h
    return(int(dp), int(hp), l)


def tuple2gradep(el,tuples):
    (db,de,hb,he)=el
    (dw,dp,rel,hw,hp)= tuples[el]
    dep = getloc(db,de)
    hd = getloc(hb,he)
    return(dep,hd,rel)

def getloc(b,e):
    if int(e)-int(b) == 1:
        result = e
    else:
        result = str(int(b)+1)+possep+e
    return(result)


def gralist2str(gralist):
    result = ""
    for (d,h,rel) in gralist:
        depstr = d+grasep+h+grasep+rel+space
        result += depstr
    #add GRA prefix
    result = graprefix+result
    return(result)


