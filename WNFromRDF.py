import re
import sys
import getopt
import sqlite3
from urllib import unquote_plus
from os import unlink
import wn_schema

lemon = "<http://lemon-model.net/lemon#"
wn_ontology = "<http://wordnet-rdf.princeton.edu/ontology#"
rdfs = "<http://www.w3.org/2000/01/rdf-schema#"
rdf  = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#"
wn_version = "wn31"

## General parsing functions
def get_synset_id(uri):
    """
    @param uri: A <> enclosed URI
    @return The synset identifier (as Int) or None if this is not a synset URI
    """
    m = re.findall("<.*" + wn_version + "\-(\d{9})\-[nvarsp]>", uri)
    if m:
        return int(m[0])
    else:
        return None

def get_lemma(uri):
    """
    @param uri: A <> enclosed URI
    @return The lemma or None if this is not an entry URI
    """
    m = re.findall("<.*/([A-Za-z0-9+_%\-\.]+)\-[nvarsp](#.*)?>", uri)
    if m:
        return unquote_plus(m[0][0])
    else:
        return None

def get_lemma_pos(uri):
    """
    @param uri: A <> enclosed URI
    @return The lemma or None if this is not an entry URI
    """
    m = re.findall("<.*/([A-Za-z0-9+_%\-\.]+\-[nvarsp])(#.*)?>", uri)
    if m:
        return unquote_plus(m[0][0])
    else:
        return None


def fragment(uri):
    """
    @param uri: A <> enclosed URI
    @return The fragment identifier with _ substituted for " "
    """
    return uri[uri.index('#') + 1: uri.index('>')].replace("_"," ")

def lang_literal(lit):
    """
    @param lit: An NT literal with a lang tag
    @return The text of the literal
    """
    return lit[lit.index('"') + 1: lit.index('@') - 1]

def int_literal(lit):
    """
    @param lit: An NT literal with integer datatype annotation
    @return The value of the integer
    """
    return int(lit[1:lit.index('^') - 1])

def string_literal(lit):
    """
    @param lit: A bare NT literal
    @return The value of the literal
    """
    lit = lit.strip()
    if '^' in lit:
        return lit[1:lit.index('^') - 1]
    else:
        return lit[1:-1]

def remap_sense(uri):
    """
    @param uri: A <> enclosed URI
    @return Assuming this is sense, the sense identifier as in the SQLite database
    """
    return get_lemma(uri).lower() + '#' + fragment(uri).replace('-',':')

## Manage static types and ids
def lexdomain_id(uri):
    """
    @param uri: A <> enclosed URI
    @return The lexdomain identifier as in the SQLite database
    """
    return wn_schema.lexdomains[fragment(uri)][0]

sample_counts = dict()
def sample_count(synsetid):
    """
    @param synsetid: The synsetid (as Int)
    @return The number of samples for this synset seen so fat
    """
    if synsetid not in sample_counts:
        sample_counts[synsetid] = 1
        return 1
    else:
        sample_counts[synsetid] += 1
        return sample_counts[synsetid]

## SQL statement generation
def sql_synsets(synsetid, pos, lexdomainid, definition):
    """
    @param synsetid: (Int)
    @param pos: (1-Char String)
    @param lexdomainid: (Int)
    @param definition: (String)
    """
    print "insert into synsets (synsetid, pos, lexdomainid, definition) values (%d,'%s',%d,\"%s\");" % (synsetid, pos, lexdomainid, definition)

def sql_phrasetypes(synsetid, phrasetype):
    """
    @param synsetid: (Int)
    @param phrasetype: (String)
    """
    print "insert into phrasetypes (synsetid, phrasetype) values (%d,'%s')" % (synsetid, phrasetype)

def sql_samples(synsetid, samplecount, sample):
    """
    @param synsetid: (Int)
    @param samplecount: (Int)
    @param sample: (String)
    """
    print "insert into samples (synsetid, sampleid, sample) values (%d, %d, \"%s\");" % (synsetid, samplecount, sample)

def sql_semlinks(synset1id, synset2id, linktype):
    """
    @param synset1id: (Int)
    @param synset2id: (Int)
    @param linktype: (String)
    """
    print "insert into semlinks (synset1id, synset2id, linkid) values (%d,%d,%d);" % (int(synset1id), int(synset2id), wn_schema.linktypes[linktype][0])

words = dict()
def sql_words(word):
    """
    @param word: (String, lowercase)
    @return The word id
    """
    if word not in words:
        words[word] = len(words) + 1
        print "insert into words (wordid, lemma) values (%d, \"%s\");" % (len(words), word)
        return len(words)
    else:
        return words[word]

casedwords = dict()
def sql_casedwords(word, wordid):
    """
    @param word: (String)
    @param wordid: As returned by sql_words
    @return The cased word id
    """
    if word not in casedwords:
        casedwords[word] = len(casedwords) + 1
        print "insert into casedwords (casedwordid, wordid, cased) values (%d,%d,\"%s\");" % (wordid, len(casedwords), word)
        return len(casedwords)
    else:
        return casedwords[word]

n_morphs = 1
def sql_morphs(wordid, pos, morph):
    """
    @param wordid: (Int) see sql_words
    @param pos: (1-Char String)
    @param morph: (String)
    """
    global n_morphs
    print "insert into morphmaps (wordid, pos, morphid) values (%d, '%s', %d);" % (wordid, pos, n_morphs)
    print "insert into morphs (morphid, morph) values (%d, \"%s\");" % (n_morphs, morph)
    n_morphs += 1

def sql_senses(uri, senses_synsetid, senses_sensenum, senses_lexid, senses_tagcount, senses_old_sensekey):
    """
    Note this only generates a statement if all maps contain a value for this URI
    @param uri: A <> enclosed URI
    """
    if uri in senses_synsetid and \
        uri in senses_sensenum and \
        uri in senses_lexid and \
        uri in senses_tagcount and \
        uri in senses_old_sensekey:
        lemma = get_lemma(uri)
        wordid = sql_words(lemma.lower())
        if lemma != lemma.lower():
            casedwordid = str(sql_casedwords(lemma, wordid))
        else:
            casedwordid = "NULL"

        print "insert into senses (wordid, casedwordid, synsetid, sensenum, lexid, tagcount, old_sensekey, sensekey) values (%d,%s,%d,%d,%d,%d,\"%s\",\"%s\");" % (wordid, casedwordid, senses_synsetid[uri], senses_sensenum[uri], senses_lexid[uri], senses_tagcount[uri], senses_old_sensekey[uri], remap_sense(uri))
        del senses_synsetid[uri]
        del senses_sensenum[uri]
        del senses_lexid[uri]
        del senses_tagcount[uri]
        del senses_old_sensekey[uri]

def sql_adjpositions(uri, adjposition, postponed):
    """
    @param uri: A <> enclosed URI
    @param adjpostion: (String)
    @param postponed: The writer for postponed SQL actions
    """
    senseid = remap_sense(uri)
    postponed.write("insert into adjpositions (synsetid, wordid, position) select synsetid, wordid, '%s' from senses where sensekey=\"%s\";\n" % (wn_schema.adjpositiontypes[adjposition], senseid))

def sql_vframesentences(uri, sentence, postponed):
    """
    @param uri: A <> enclosed URI
    @param sentence: (String) must be in wn_schema.vframesenteces
    @param postponed: The writer for postponed SQL actions
    """
    vframeid = wn_schema.vframesentences[sentence.replace("\\\"","\"")]
    senseid = remap_sense(uri)
    postponed.write("insert into vframesentencemaps (synsetid, wordid, sentenceid) select synsetid, wordid, %d from senses where sensekey=\"%s\";\n" % (vframeid,senseid))

def sql_lexlinks(subj, pred, obj, postponed):
    """
    @param subj: A <> enclosed URI
    @param pred: A <> enclosed URI
    @param obj: A <> enclosed URI
    @param postponed: The writer for postponed SQL actions
    """
    senseid1 = remap_sense(subj)
    senseid2 = remap_sense(obj)
    pred = wn_schema.linktypes[fragment(pred)][0]
    postponed.write("insert into lexlinks (senseid1, senseid2, linkid) select (select senseid from senses where sensekey=\"%s\") as senseid1, "
            "(select senseid from senses where sensekey=\"%s\") as senseid2, %d;\n" % (senseid1,senseid2,pred))

n_sensetags = 1
def sql_sensetag(uri, target, postponed):
    """
    @param uri: The uri of the sense that this tag
    @param target: The target of the sensetag (i.e., the phrase)
    @param postponed: The writer for postponed SQL actions
    """
    global n_sensetags
    position = int(target[target.rindex('-') + 1: -2 ])
    lemma = get_lemma(uri)
    senseid = remap_sense(uri)
    target_senseid = get_lemma(target).replace(" ","_") + "#1:p"
    postponed.write("insert into sensetags (sensetagid, sensekey, new_sensekey) select %d, old_sensekey, sensekey from senses where sensekey=\"%s\";\n" % (n_sensetags, senseid))
    postponed.write("insert into taggedtexts (wordid, casedwordid, sensetagid, position, senseid ) select wordid, casedwordid, %d, %d, (select senseid from senses where sensekey=\"%s\") from sense where sensekey=\"%s\";\n" % (n_sensetags, position, target_senseid, senseid))
    n_sensetags += 1


def sql_synsettriples(subj, pred, obj):
    synsetid = get_synset_id(subj)
    print "insert into synsettriples ( synsetid, property, object ) values ( %d, '%s', '%s' );" % (synsetid, pred[1:-1], obj.replace("'","''"))

def sql_entrytriples(subj, pred, obj):
    lemma = get_lemma_pos(subj)
    if '#' in subj:
        frag = fragment(subj)
        print "insert into entrytriples ( lemma, fragment, property, object ) values ( '%s', '%s', '%s', '%s' );" % (lemma.replace("'","''"), frag, pred, obj.replace("'","''"))
    else:
        print "insert into entrytriples ( lemma, fragment, property, object ) values ( '%s', NULL, '%s', '%s' );" % (lemma.replace("'","''"), pred, obj.replace("'","''"))

        

## Write the static wn schema
def write_wn_schema():
    print "CREATE TABLE IF NOT EXISTS [synsettriples] ([synsetid] INTEGER NOT NULL REFERENCES [synsets] ([synsetid]), property VARCHAR(80) NOT NULL, object VARCHAR(80) NOT NULL);"
    print "CREATE INDEX IF NOT EXISTS k_synsettriples_synsetid ON [synsettriples] ( synsetid ); "
    print "CREATE TABLE IF NOT EXISTS [entrytriples] ([lemma] VARCHAR(80), [fragment] VARCHAR(80), property VARCHAR(80) NOT NULL, object VARCHAR(80) NOT NULL);"
    print "CREATE INDEX IF NOT EXISTS k_entrytriples_lemma ON [entrytriples] ( lemma ); "
    for key,(lexdomain_id, pos) in wn_schema.lexdomains.items():
        print "insert into lexdomains ( lexdomainid, lexdomainname, pos ) values ( %d, '%s', '%s' );" % (lexdomain_id, key, pos)
    for positionname, position in wn_schema.adjpositiontypes.items():
        print "insert into adjpositiontypes ( position, positionname ) values ( '%s', '%s' );" % (position, positionname)
    for link, (linkid, recurses, linktype) in wn_schema.linktypes.items():
        print "insert into linktypes ( linkid, link, recurses, linktype ) values ( %d, '%s', %d, '%s' );" % ( linkid, link, recurses, linktype )
    for posname, pos in wn_schema.postypes.items():
        print "insert into postypes ( pos, posname ) values ( '%s', '%s' );" % ( pos, posname )
    for sentence, sentenceid in wn_schema.vframesentences.items():
        print "insert into vframesentences ( sentenceid, sentence ) values ( %d, '%s' );" % ( sentenceid, sentence.replace("'","''") )

## Main reading loop
def read_from_nt(nt, postponed):
    """
    @param nt: An open stream of n-triple lines
    @param postponed: An open stream to write postponed actions to
    """
    synset_id_lexdomain = dict()
    synset_id_definition = dict()
    senses_synsetid = dict()
    senses_sensenum = dict()
    senses_tagcount = dict()
    senses_lexid = dict()
    senses_old_sensekey = dict()
    synset_word_senses = dict()
    for line in nt:
        # Basic n-triples validation
        line = line.strip()
        if line == "":
            continue
        elems = re.split(" ", line)
        subj = elems[0]
        if not subj.startswith("<") and not subj.endswith(">"):
            print line
            raise Exception("Bad subject")
        pred = elems[1]
        if not pred.startswith("<") and not pred.endswith(">"):
            print line
            raise Exception("Bad predicate")
        if elems[-1].endswith('.'):
            obj = " ".join(elems[2:])
            obj = obj[:-1].strip()
        else:
            if not "." in elems:
                print line 
                raise Exception("No . at end of line")
            obj = " ".join(elems[2:elems.index('.')])
        # Switch on the predicate type
        if pred == (rdf + "type>"):
            pass
        elif pred == (wn_ontology + "part_of_speech>"):
            if get_synset_id(subj):
                pass
            elif get_lemma(subj):
                pass
            else:
                print line
                raise Exception("Unrecognized triple")
        elif pred == (wn_ontology + "lexical_domain>"):
            synset_id = get_synset_id(subj)
            if synset_id in synset_id_definition: 
                sql_synsets(synset_id, subj[-2], lexdomain_id(obj), synset_id_definition[synset_id])
                del synset_id_definition[synset_id]
            else:
                synset_id_lexdomain[synset_id] = lexdomain_id(obj)
        elif pred == (wn_ontology + "gloss>"):
            if get_synset_id(subj):
                synset_id = get_synset_id(subj)
                if synset_id in synset_id_lexdomain:
                    sql_synsets(synset_id, subj[-2], synset_id_lexdomain[synset_id], lang_literal(obj))
                    del synset_id_lexdomain[synset_id]
                else:
                    synset_id_definition[synset_id] = lang_literal(obj)
            else:
                pass
        elif pred == (wn_ontology + "phrasetype>"):
            sql_phrasetypes(int(get_synset_id(subj)[0]), fragment(obj))
        elif pred == (rdfs + "label>"):
            pass
        elif pred == (wn_ontology + "synset_member>"):
            pass
        elif pred == (wn_ontology + "sample>"):
            synsetid = get_synset_id(subj)
            sql_samples(synsetid, sample_count(synsetid), lang_literal(obj))
        elif get_synset_id(subj) and pred.startswith(wn_ontology) and get_synset_id(obj):
            semlink = fragment(pred)
            sql_semlinks(get_synset_id(subj), get_synset_id(obj), semlink)
        elif pred == (lemon + "canonicalForm>"):
            pass
        elif pred == (lemon + "otherForm>"):
            pass
        elif pred == (lemon + "writtenRep>"):
            if fragment(subj) == "CanonicalForm":
                lemma = lang_literal(obj)
                if lemma == lemma.lower():
                    sql_words(lang_literal(obj))
                else:
                    wordid = sql_words(lemma.lower())
                    sql_casedwords(lemma, wordid)
            else:
                lemma = get_lemma(subj)
                wordid = sql_words(lemma)
                sql_morphs(wordid,subj[subj.index('#')-1],lang_literal(obj))
        elif pred == (lemon + "sense>"):
            pass
        elif pred == (lemon + "reference>"):
            senses_synsetid[subj] = get_synset_id(obj)
            sql_senses(subj,senses_synsetid, senses_sensenum, senses_lexid, senses_tagcount, senses_old_sensekey)
        elif pred == (wn_ontology + "sense_number>"):
            senses_sensenum[subj] = int_literal(obj)
            sql_senses(subj,senses_synsetid, senses_sensenum, senses_lexid, senses_tagcount, senses_old_sensekey)
        elif pred == (wn_ontology + "tag_count>"):
            senses_tagcount[subj] = int_literal(obj)
            sql_senses(subj,senses_synsetid, senses_sensenum, senses_lexid, senses_tagcount, senses_old_sensekey)
        elif pred == (wn_ontology + "lex_id>"):
            senses_lexid[subj] = int_literal(obj)
            sql_senses(subj,senses_synsetid, senses_sensenum, senses_lexid, senses_tagcount, senses_old_sensekey)
        elif pred == (wn_ontology + "old_sense_key>"):
            senses_old_sensekey[subj] = string_literal(obj)
            sql_senses(subj,senses_synsetid, senses_sensenum, senses_lexid, senses_tagcount, senses_old_sensekey)
        elif pred == (wn_ontology + "adjposition>"):
            sql_adjpositions(subj,fragment(obj), postponed)
        elif pred == (wn_ontology + "verb_frame_sentence>"):
            sql_vframesentences(subj,lang_literal(obj), postponed)
        elif pred == (wn_ontology + "sense_tag>"):
            sql_sensetag(subj, obj, postponed)
        elif get_lemma(subj) and pred.startswith(wn_ontology) and get_lemma(wn_ontology): # Assume this is a lex-link
            sql_lexlinks(subj,pred,obj,postponed)
        elif get_synset_id(subj):
            sql_synsettriples(subj,pred,obj)
        elif get_lemma(subj):
            sql_entrytriples(subj,pred,obj)
        else:
            print line
            raise Exception("Unrecognized triple")
            

# Usage:
#   python WNFromRDF.py [-h] < wordnet.nt
#   Specify -h to also populate the static tables (i.e., from wn_schema.py)
if __name__ == '__main__':
    opts = dict(getopt.getopt(sys.argv[1:],'h')[0])
    if '-h' in opts:
        write_wn_schema()
    postponed = open("postponed.sql","w")
    print("begin transaction;")
    read_from_nt(sys.stdin,postponed)
    postponed.flush()
    postponed.close()
    print("commit transaction;")
    print("begin transaction;")
    postponed = open("postponed.sql","r")
    for line in postponed:
        print line.strip()
    postponed.close() 
    unlink("postponed.sql")
    print("commit transaction;")
