import sys
import codecs
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree
from xml.etree.ElementTree import parse
#from xml.etree.ElementTree import iter


program_name = sys.argv[0]
baseversion = "0"
subversion = "13"
version = baseversion +  "." + subversion

complementrels = {'su', 'obj1', 'obj2', 'vc', 'pc', 'ld', 'me', 'predc', 'pobj1','se', 'sup', 'svp'}
modrels = ['mod', 'predm', 'obcomp']

attvals = [ ('rel', [ 'app', 'det', 'hdf', 'su', 'obcomp', 'obj1', 'obj2', 'vc', 'pc', 'ld', 'me', 'predc', 'pobj1','se', 'sup', 'svp', 
                      'mod', 'predm', 'hd', 'cmp', 'crd', 'dlink', 'rhd', 'whd', 'body', 'nucl', 'cnj', 'dp', 'sat', 'tag', '--']),
            ('cat', ['advp', 'ahi', 'ap', 'conj', 'cp', 'detp', 'du', 'inf', 'mwu', 'np', 'oti', 'pp', 'ppart', 'ppres', 'rel', 'smain', 
                     'ssub', 'sv1', 'svan', 'ti', 'top', 'whq', 'whrel', 'whsub'])
		  ] 
#heads=['hd', 'cmp', 'crd', 'dlink', 'rhd', 'whd']
caheads={'hd':1, 'cmp':2, 'crd':3, 'dlink':4, 'body':5, 'rhd':6 , 'whd':7, 'nucl':8}
rootheads={'hd':1, 'cmp':2, 'crd':3, 'dlink':4, 'body':5, 'nucl':6, 'dp':7}
heads = caheads
rootposcats = ["TSW()", "LET()"]
neverheads = ["TSW()", "LET()"]

# syntactic categories that we want to count as a single word
mwus= ['mwu']
cnjs=['cnj']
crds = ['crd']
excludefiles=[]
excludeposcats = ["TSW()", "LET()"]
boringrelations = ['--/--']


rootrel = 'ROOT'
unknownpostag = 'NA()'

dpset = ['dp']  # relations for discourse fragments
duset = ['du'] # categgories for discourse units


themode = "triples"
global indexednodes
indexednodes = {}


def utf8(str):
    return (str.encode('utf8'))


def reducetuples(tuples, excludelist):
    result = {}
    for el in tuples:
        (dw, dp, rel, hw, hp) = tuples[el]
        if dp not in excludelist and hp not in excludelist:
            result[el] = tuples[el]
    return (result)


def getMWUWordstr(node):
    result = ""
    themwu = {}
    for descendant in node.iter():
        datt = node.attrib
        if ('pt' in datt or 'pos' in datt) and 'end' in datt:
            themwu[datt['end']] = datt['word']
    for i in sorted(themwu):
        if result == "":
            result = themwu[i]
        else:
            result = result + space + themwu[i]
        # print(i, themwu[i],result, file=logfile)
    result = "<" + result + ">"
    return result


def getWordstr(node):
    result = ""
    att = getAttrib(node)
    if 'pt' in att:
        result = att['word']
    elif 'pos' in att:
        result = att['word']
    elif 'cat' in att and att['cat'] in mwus:
        result = getMWUWordstr(node)
    else:
        result = "@@unknown@@"
    return (result)


def compose(str1, str2):
    result = str1 + "/" + str2
    return (result)


def getPosCat(node):
    if node is not None:
        att = getAttrib(node)
        if 'pt' in att:
            result = att['pt']
        elif 'pos' in att:
            result = att['pos']
        elif 'cat' in att:
            result = att['cat']
        else:
            result = "unknown node"
    else:
        result = "None node"
    return (result)


def getLongPosCat(node):
    if node is not None:
        att = getAttrib(node)
        if 'pt' in att:
            if 'postag' in att:
                result = att['postag']
            else:
                result = unknownpostag
        elif 'pos' in att:
            if 'postag' in att:
                result = unknownpostag
            else:
                result = att['pos']
        elif 'cat' in att:
            result = att['cat']
        else:
            result = "unknown node"
    else:
        result = "None node"
    return (result)


def show(node):
    result = ""
    if 'pt' in node.attrib:
        result = node.attrib['pt'] + "/" + node.attrib['word']
    elif 'cat' in node.attrib:
        result = node.attrib['cat']
    elif 'index' in node.attrib:
        result = "index:" + node.attrib['index']
    else:
        result = "unknown node:"
    return (result)


# only defined for nodes with 'cat' attribute
def getBeginEndNonterminal(node):
    begin = 999999
    end = 0
    if 'cat' in node.attrib:
        for descendant in node.iter():
            datt = descendant.attrib
            if ('pt' in datt or 'pos' in datt) and 'end' in datt and int(datt['end']) > end: end = int(datt['end'])
            if ('pt' in datt or 'pos' in datt) and 'begin' in datt and int(datt['begin']) < begin: begin = int(
                datt['begin'])
    beginstr = str(begin)
    endstr = str(end)
    return (beginstr, endstr)


def getMWUattrib(node):
    attrib = {}
    attrib['word'] = getMWUWordstr(node)
    (begin, end) = getBeginEndNonterminal(node)
    attrib['begin'] = begin
    attrib['end'] = end
    attrib['rel'] = node.attrib['rel']
    attrib['cat'] = node.attrib['cat']
    return (attrib)


def noposcatin(node):
    result = 'pt' not in node.attrib and 'pos' not in node.attrib and 'cat' not in node.attrib
    return result


def nobeginendin(node):
    result = 'begin' not in node.attrib and 'end' not in node.attrib
    return result


def getAttrib2(node, indexednodes):
    result = None
    if 'index' in node.attrib and noposcatin(node):
        resultnode = indexednodes[node.attrib['index']]
        result = resultnode.attrib
        result['rel'] = node.attrib['rel']
    elif 'pt' in node.attrib or 'pos' in node.attrib:
        result = node.attrib
    elif 'cat' in node.attrib and node.attrib['cat'] in mwus:
        result = getMWUattrib(node)
    elif 'cat' in node.attrib:
        result = node.attrib
    else:  # should not occur
        result = None
    return (result)


def getFullNode(node, indexednodes):
    if 'index' in node.attrib and noposcatin(node):
        resultnode = indexednodes[node.attrib['index']]
    else:
        resultnode = node
    return resultnode


def getAttrib(node):
    result = None
    if 'index' in node.attrib and noposcatin(node):
        resultnode = indexednodes[node.attrib['index']]
        result = resultnode.attrib
        result['rel'] = node.attrib['rel']
    elif 'pt' in node.attrib or 'pos' in node.attrib:
        result = node.attrib
    elif 'cat' in node.attrib and node.attrib['cat'] in mwus:
        result = getMWUattrib(node)
    elif 'cat' in node.attrib:
        result = node.attrib
    else:  # should not occur
        result = None
    return (result)


def getWords(node,logfile):
    # print( "GetWords", file=logfile)
    # print("node=", show(node), file=logfile)
    results = []
    if node is None:
        # print("getWords: node is None", file=logfile)
        pass
    else:
        if 'pt' in node.attrib:
            results.append(node)
        elif 'pos' in node.attrib:
            results.append(node)
        elif 'cat' in node.attrib and node.attrib['cat'] in mwus:
            results.append(node)
        elif 'cat' in node.attrib:
            # recursion elaborate
            (headfound, newhead) = getHead(node)
            if headfound:
                results = results + getWords(newhead, logfile)
            else:
                for child in node:
                    results = results + getWords(child,logfile)
            if headfound and getAttrib(newhead)['rel'] in crds:
                for child in node:
                    if getAttrib(child)['rel'] in cnjs:
                        results = results + getWords(child, logfile)
        elif 'index' in node.attrib:
            theindex = node.attrib['index']
            if theindex in indexednodes:
                antnode = indexednodes[theindex]
            else:
                antnode = None
                print("Antecedent for index {} lacking in {}".format(theindex, node), file=logfile)
            thewords = getWords(antnode, logfile)
            for theword in thewords:
                results.append(theword)
        else:  # should not occur
            pass
    # print( "GetWords", file=logfile)
    # for r in results:
    #    print(show(r), file=logfile)
    # print (input("Continue?"))
    return (results)

def tuples2triples(tuples):
    result=[]
    for el in tuples:
        (db,de,hb,he)=el
        (dw,dp,rel,hw,hp)= tuples[el]
        triple=(de,rel,he)
        result.append(triple)
    return(result)



def getHead(node):
    result = False
    foundhead = None
    hdrank = 100
    # print("getHead")
    # print("node=",show(node))
    for child in node:
        # print("child=", show(child))
        if 'rel' in child.attrib:
            if child.attrib['rel'] in heads:
                newrank = heads[child.attrib['rel']]
                if newrank < hdrank:
                    foundhead = child
                    result = True
                    hdrank = newrank
    # print(input('getHead: Continue?'))
    # print( "getHead, file=logfile)
    # print(show(foundhead), file=logfile)
    return ((result, foundhead))


def getTuples(fullname, logfile, mode, tuples, strict, utterance=False):
    global indexednodes
    with codecs.open(fullname, 'r', encoding='utf8') as thefile:
        tree = ET.parse(thefile)
        toproot = tree.getroot()
        # get the yield of the tree if utterance = True @@still to be implemented
        if utterance:
            sentence = toproot.find("sentence").text
        else:
            sentence = ''

        # the topnode is alpino_ds with node, sentence and comments as children
        root = toproot.find("node")

        # first gather all indexed nodes and their attributes
        indexednodes = {}
        for node in root.iter():
            if 'index' in node.attrib and ('pt' in node.attrib or 'cat' in node.attrib or 'pos' in node.attrib):
                theindex = node.attrib['index']
                indexednodes[theindex] = node
        # print("indexednodes:")
        # for i in indexednodes:
        #   print(i, indexednodes[i])

        getTriples(fullname, logfile, root, mode, tuples, strict)

        rootsfound = addRoots(fullname, logfile, root, tuples)

        #if not rootsfound:
        #    print('No root found: {}'.format(fullname), file=logfile)
        return (sentence)


def getTriples(fullname, logfile, node, mode, tuples, strict):
    (headfound, h) = getHead(node)
    if headfound:
        hws = getWords(h,logfile)
        for hw in hws:
            for child in node:
                if child != h:
                    dws = getWords(child, logfile)
                    for dw in dws:
                        hwatt = getAttrib(hw)
                        dwatt = getAttrib(dw)
                        hposcat = getLongPosCat(hw) if strict else getPosCat(hw)
                        dposcat = getLongPosCat(dw) if strict else getPosCat(dw)
                        therel = child.attrib['rel']
                        hwword = getWordstr(hw)
                        dwword = getWordstr(dw)
                        # print("hwatt=", hwatt)
                        # print("dwatt=", dwatt)
                        # print("'debug:", dwatt['end'], hwatt['end'], therel)
                        if testatts(fullname, [dwatt, hwatt], ['begin', 'end']):
                            tuples[(dwatt['begin'], dwatt['end'], hwatt['begin'], hwatt['end'])] = (
                            dwword, dposcat, therel, hwword, hposcat)
                            # print(dwatt['end'], hwatt['end'], utf8(dwword), utf8(dposcat), utf8(therel), utf8(hwword), utf8(hposcat))
    else:
        excluded = []
        for child1 in node:
            excluded.append(child1)
            # print("node=",show(node), file=logfile)
            # print("child1=",show(child1), file=logfile)
            rel1 = child1.attrib['rel']
            for child2 in node:
                if child2 not in excluded:
                    rel2 = child2.attrib['rel']
                    ws1 = getWords(child1, logfile)
                    ws2 = getWords(child2, logfile)
                    for w1 in ws1:
                        for w2 in ws2:
                            w1att = getAttrib(w1)
                            w2att = getAttrib(w2)
                            w1poscat = getLongPosCat(w1) if strict else getPosCat(w1)
                            w2poscat = getLongPosCat(w2) if strict else getPosCat(w2)
                            w1word = getWordstr(w1)
                            w2word = getWordstr(w2)
                            # normalize this tuple LET() and TSW() always as dependent otherwise word with lowest end is considered the dependent
                            dwatt = {}
                            hwatt = {}
                            if w2poscat in neverheads and w1poscat not in neverheads:
                                switch = True
                            elif w1att['end'] > w2att['end']:
                                switch = True
                            else:
                                switch = False
                            if not switch:
                                dwatt['begin'] = w1att['begin']
                                dwatt['end'] = w1att['end']
                                hwatt['begin'] = w2att['begin']
                                hwatt['end'] = w2att['end']
                                dwposcat = w1poscat
                                hwposcat = w2poscat
                                dwword = w1word
                                hwword = w2word
                                composedrel = compose(rel1, rel2)
                            else:
                                dwatt['begin'] = w2att['begin']
                                dwatt['end'] = w2att['end']
                                hwatt['begin'] = w1att['begin']
                                hwatt['end'] = w1att['end']
                                dwposcat = w2poscat
                                hwposcat = w1poscat
                                dwword = w2word
                                hwword = w1word
                                composedrel = compose(rel2, rel1)
                            tuples[(dwatt['begin'], dwatt['end'], hwatt['begin'], hwatt['end'])] = (
                            dwword, dwposcat, composedrel, hwword, hwposcat)
                            # print(w2att['end'], w1att['end'], utf8(w2word), utf8(w2poscat), utf8(composedrel), utf8(w1word), utf8(w1poscat))

    # and do this for all children - recursion step
    for child in node:
        if 'cat' in child.attrib and child.attrib['cat'] not in mwus:
            # print(show(child), file=logfile)
            getTriples(fullname, logfile, child, mode, tuples, strict)

    # tuples for single word utterances
    if tuples == {}:
        singlewordutt(fullname, node, mode, tuples, strict,logfile)


def singlewordutt(fullname, node, mode, tuples, strict, logfile):
    thewordnodes = getWords(node, logfile)
    for w in thewordnodes:
        watt = getAttrib(w)
        wb = watt['begin']
        we = watt['end']
        wposcat = getLongPosCat(w) if strict else getPosCat(w)
        wword = getWordstr(w)
        tuples[(wb, we, '-1', '0')] = (wword, wposcat, rootrel, '', '')

def islexical(node):
    atts =getAttrib(node)
    result = atts is not None and 'pt' in atts or 'pos' in atts
    return result

def getExt(file):
    (base, ext) = os.path.splitext(file)
    return (ext)


def mwetuple(x):
    (dw, dposcat, rel, hw, hposcat) = x
    return (dposcat, hposcat)


def myshow(tuple, mwe1, mwe2):
    (db, de, hb, he) = tuple
    if mwe1 in mwus:
        first = db + "-" + de
    else:
        first = de
    if mwe2 in mwus:
        second = hb + "-" + he
    else:
        second = he
    result = first + "<>" + second
    return (result)


def addRoots(fullname, logfile, root,tuples):
    result = False
    (result, thehead) = getLexHead(root)
    if result:
        addroottuple(tuples, thehead)
    elif dufound(root):
        for child in root:
            if isadu(child):
                result3 = addRoots(fullname, logfile, child,tuples)
                result = result or result3
                if not result:
                    for grandchild in child:
                        if isadp(grandchild):
                            result2= addRoots(fullname, logfile, grandchild,tuples)
                            result = result or result2
                        if isadp(grandchild) and islexical(grandchild):
                            addroottuple(tuples, grandchild)
                            result = True
    return result

def addroottuple(tuples, node):
    atts = getAttrib(node)
    hb = atts['begin']
    he = atts['end']
    hw = atts['word']
    hp = atts['pt']
    tuples[(hb, he, '-1', '0')] = (hw, hp, rootrel, '', '')


def getLexHead(root):
    if root is None:
        (result, thehead) = (False, None)
    else:
        (result,thehead) = getHead(root)
        #print(result, thehead)
        if result:
            atts =getAttrib(thehead)
            if not('pt' in atts):
                (result, thehead) = getLexHead(thehead)
        else:
            for child in root:
                chatts = getAttrib(child)
                if (not result) and chatts is not None and 'rel' in chatts and chatts['rel'] == '--':
                    (result,thehead) = getLexHead(child)
    return(result,thehead)


def testatts(fullname, dicts, atts):
    result = True
    for thedict in dicts:
        for theatt in atts:
            if theatt not in thedict:
                result = False
                print('Error: Attribute {} not in dict {}, file {}'.format(theatt, thedict, fullname), file=testgralogfile)
    return result

def dufound(node):
    result = False
    for child in node:
        if not result:
            result = isadu(child)
    return result

def isadp(node):
    result= False
    atts = getAttrib(node)
    result = atts is not None and 'rel' in atts and atts['rel'] in dpset
    return result

def isadu(node):
    result= False
    atts = getAttrib(node)
    result = atts is not None and 'cat' in atts and atts['cat'] in duset
    return result