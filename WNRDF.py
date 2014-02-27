from rdflib import *
from rdflib.util import from_n3
from urllib import quote_plus
import sqlite3
import sys
import getopt

__author__ = 'jmccrae'

prefix = "http://wordnet-rdf.princeton.edu/"
lemon = Namespace("http://www.monnet-project.eu/lemon#")
wn_ontology = Namespace("http://wordnet-rdf.princeton.edu/ontology#")
wn_version = "wn31"


class WNRDFContext:
    """
    This object avoids some queries to the database
    by pre-querying some small tables, e.g., link types
    """
    def __init__(self, db_name, lang='eng'):
        self.lang = lang
        self.jsonld_context = {
            "@language": lang,
            "label": "http://www.w3.org/2000/01/rdf-schema#label",
            "wordnet": prefix,
            "wordnet-ontology": str(ontology_name("")),
            "lemon": str(lemon),
            "wordnet-ontology:lexical_domain": {
                "@id": str(ontology_name("lexical_domain")),
                "@type": "@id"
            },
            "wordnet-ontology:word": {
                "@id": str(ontology_name("word")),
                "@type": "@id"
            },
            "wordnet-ontology:part_of_speech": {
                "@id": str(ontology_name("part_of_speech")),
                "@type": "@id"
            },
            "lemon:otherForm": {
                "@id": str(lemon.otherForm),
                "@type": "@id"
            },
            "lemon:canonicalForm": {
                "@id": str(lemon.canonicalForm),
                "@type": "@id"
            },
            "lemon:sense": {
                "@id": str(lemon.sense),
                "@type": "@id"
            },
            "lemon:reference": {
                "@id": str(lemon.reference),
                "@type": "@id"
            },
            "wordnet-ontology:gloss": {
                "@id": str(ontology_name("gloss"))
            }
        }
        self.conn = sqlite3.connect(db_name)
        cursor = self.conn.cursor()
        cursor.execute("select * from lexdomains")
        self.lexdomainid_to_name = dict()
        for lexdomainid, lexdomainname, _ in cursor.fetchall():
            self.lexdomainid_to_name[lexdomainid] = lexdomainname
        cursor.execute("select * from adjpositiontypes")
        self.adjposition_names = dict()
        for position, positionname in cursor.fetchall():
            self.adjposition_names[position] = positionname.replace(" ", "_")
        cursor.execute("select linkid, link from linktypes")
        self.linktypes = dict()
        for linkid, link in cursor.fetchall():
            link_name = link.replace(" ", "_")
            self.linktypes[linkid] = link_name
            self.jsonld_context["wordnet-ontology:" + link_name] = {
                "@id": str(ontology_name(link_name)),
                "@type": "@id"
            }
        cursor.execute("select pos, posname from postypes")
        self.postypes = dict()
        for pos, posname in cursor.fetchall():
            self.postypes[pos] = posname.replace(" ", "_")
            # Load this into memory as there is no index :s
        cursor.execute("select * from vframesentences")
        self.vframesentences = dict()
        for sentenceid, sentence in cursor.fetchall():
            self.vframesentences[sentenceid] = sentence

    def __del__(self):
        self.conn.close()

    def dump(self, file, verbose=False, limit=-1):
        """
        Convert all the data in the database to N-Triples
        @param file: The file to write to
        @param verbose: Say what we are doing
        @param limit: The maximum number of synsets/words to write or -1 for no limit
        """
        f = open(file, 'w')
        if limit < 0:
            limit_string = ""
        else:
            limit_string = " limit %d" % limit
        cursor = self.conn.cursor()
        cursor.execute("select synsetid from synsets" + limit_string)
        for synsetid, in cursor.fetchall():
            graph = synset(self, synsetid)
            graph.serialize(f, "nt")
            if verbose:
                print(synsetid)
        cursor.execute(
            "select pos,lemma,words.wordid from synsets inner join senses, words on synsets.synsetid = senses.synsetid and "
            "senses.wordid = words.wordid" + limit_string)
        for pos, lemma, wordid in cursor.fetchall():
            graph = entry(self, lemma, pos)
            if graph:
                graph.serialize(f, "nt")
            cursor.execute("select cased from casedwords where wordid=?", (wordid,))
            for cased, in cursor.fetchall():
                graph = entry(self, cased, pos)
                if verbose:
                    print(cased)
                if graph: # POS may be incorrect for cased form
                    graph.serialize(f, "nt")
            if verbose:
                print (lemma)


def make_graph():
    """
    Create a graph for WNRDFs
    @rtype : A RDFLib graph
    """
    g = ConjunctiveGraph()
    g.bind("lemon", lemon)
    g.bind("wordnet-ontology", wn_ontology)
    g.bind("owl", str(OWL))
    return g


def synset_name(offset, pos):
    """
    Name a synset
    @param offset: The synset offset value
    @param pos: The part of speech (as a single letter)
    @return: A rdflib URI of the synset name
    """
    return URIRef("%s%s/%09d-%s" % (prefix, wn_version, offset, pos))


def entry_name(lemma, pos, fragment=None):
    """
    Name an entry or element of an entry
    @param lemma: The lemma (unquoted)
    @param pos: The part of speech (as a single letter)
    @param fragment: Any sub-identifier or None for no sub-identifier
    @return: A rdflib URI for this entry
    """
    if fragment is None:
        return URIRef("%s%s/%s-%s" % (prefix, wn_version, quote_plus(lemma), pos))
    else:
        return URIRef("%s%s/%s-%s#%s" % (prefix, wn_version, quote_plus(lemma), pos, fragment.replace(":", "-")))


def ontology_name(name):
    """
    Get a name of an entity in the WordNet ontology
    @param name: The name
    @return: The rdflib URI for this entity
    """
    return URIRef(prefix + "ontology#" + name.replace(" ","_"))


def translate_to_lexvo(sensekey, pos):
    lemma, key = sensekey.split('%')
    if pos == "n":
        pos = "noun"
    elif pos == "v":
        pos = "verb"
    elif pos == "a":
        pos = "adj"
    elif pos == "r":
        pos = "adv"
    elif pos == "s":
        pos = "adj"    
    key = key.replace(":","_")
    while key.endswith("_"):
        key = key[:-1]
    return URIRef("http://www.lexvo.org/page/wordnet/30/%s/%s_%s" % (pos, quote_plus(lemma), key))

def pos2number(pos):
    """
    Return the numeric part of speech or zero for unknown for a single letter code
    """
    if pos == 'n':
        return 1
    elif pos == 'v':
        return 2
    elif pos == 'a':
        return 3
    elif pos == 'r':
        return 4
    elif pos == 's':
        return 3
    elif pos == 'p':
        return 4
    else:
        return 0


def synset(context, offset, graph=None):
    """ 
    Return an RDF graph for a synset given an offset value
    @param context: A WNRDFContext object
    @param offset: The offset value in the database (Int)
    @param graph: If not None add to this graph
    @return The graph passed (or a new graph) containing the triples for this synset or None if the synset was not found
    """
    if graph is None:
        graph = make_graph()
    cursor = context.conn.cursor()

    # Read the synset information
    cursor.execute("select pos, lexdomainid, definition from synsets where synsetid=?", (offset,)) # no index
    row = cursor.fetchone()
    if row is None:
        return None
    pos, lexdomainid, definition = row
    synset_uri = synset_name(offset, pos)
    graph.add((synset_uri, RDF.type, wn_ontology.Synset))
    graph.add((synset_uri, wn_ontology.part_of_speech, wn_ontology.term(context.postypes[pos])))
    graph.add((synset_uri, wn_ontology.lexical_domain, wn_ontology.term(context.lexdomainid_to_name[lexdomainid])))
    graph.add((synset_uri, wn_ontology.gloss, Literal(definition, lang=context.lang)))

    cursor.execute("select lemma, casedwordid from senses inner join words on senses.synsetid=? and senses.wordid=words.wordid",
                   (offset,))
    for lemma, casedwordid in cursor.fetchall():
        if casedwordid:
            cursor.execute("select cased from casedwords where casedwordid=?", (casedwordid,))
            cased_lemma, = cursor.fetchone()
            graph.add((synset_uri, RDFS.label, Literal(cased_lemma, lang=context.lang)))
            graph.add((synset_uri, wn_ontology.synset_member, entry_name(cased_lemma, pos)))
        else:
            graph.add((synset_uri, RDFS.label, Literal(lemma, lang=context.lang)))
            graph.add((synset_uri, wn_ontology.synset_member, entry_name(lemma, pos)))

    # Read the phrase type (if it exists)
    cursor.execute("select phrasetype from phrasetypes where synsetid=?", (offset,)) # unindexed
    for phrasetype, in cursor.fetchall():
        graph.add((synset_uri, wn_ontology.phrase_type, wn_ontology.term(phrasetype)))

    # Read the samples
    cursor.execute("select sampleid, sample from samples where synsetid=?", (offset,))
    for sampleid, sample in cursor.fetchall():
            graph.add((synset_uri, wn_ontology.sample, Literal(sample, lang=context.lang)))

    # Read the synset links
    cursor.execute("select synset2id, linkid from semlinks where synset1id=?", (offset,))
    for synsetid2, linkid in cursor.fetchall():
        cursor.execute("select pos from synsets where synsetid=?", (synsetid2,))
        row = cursor.fetchone()
        if row is None:
            sys.stderr.write("Synset %s referred to but not found " % synsetid2)
        else:
            pos2, = row
            synset_uri2 = synset_name(synsetid2,pos2)
            graph.add((synset_uri, wn_ontology.term(context.linktypes[linkid]), synset_uri2))
    try:
        cursor.execute("select property, object from synsettriples where synsetid=?",(offset,))
        for p, o in cursor.fetchall():
            graph.add((synset_uri, URIRef(p), from_n3(o)))
    except Exception as e:
        print (e)

    return graph


def entry(context, lemma, pos, graph=None):
    """ 
    Return an RDF graph for a lexical entry given a particular lemma string
    @param context: A WNRDF Context
    @param lemma: The lemma (case-sensitive!)
    @param pos: The part-of-speech (as a 1-letter code)
    @param graph: A graph to add the triples to (or None for a new graph)
    @return The graph containing the entry's triples or None if the entry was not found
    """
    # First map the lemma to the internal word id
    if graph is None:
        graph = make_graph()
    cursor = context.conn.cursor()

    if not lemma.islower():
        cased_lemma = lemma
        lemma = lemma.lower()
    else:
        cased_lemma = lemma
    cursor.execute("select * from words where lemma=?", (lemma,))
    row = cursor.fetchone()
    if row is None:
        return None
    word_id, _ = row

    # Add entry description
    entry_uri = entry_name(cased_lemma, pos)
    graph.add((entry_uri, RDF.type, lemon.LexicalEntry))
    graph.add((entry_uri, wn_ontology.part_of_speech, wn_ontology.term(context.postypes[pos])))
    canonical_form_uri = entry_name(cased_lemma, pos, "CanonicalForm")
    graph.add((entry_uri, lemon.canonicalForm, canonical_form_uri))
    graph.add((canonical_form_uri, lemon.writtenRep, Literal(cased_lemma, lang=context.lang)))
    graph.add((canonical_form_uri, RDF.type, lemon.Form))

    # Search for morphological forms
    cursor.execute("select pos, morphid from morphmaps where wordid=? and pos=?", (word_id, pos)) # partially unindexed
    other_forms = 1
    this_pos_found = False
    for pos, morphid in cursor.fetchall():
        cursor.execute("select morph from morphs where morphid=?", (morphid,)) # unindexed
        for morph, in cursor.fetchall():
            other_form_uri = entry_name(cased_lemma, pos, "Form-%d" % other_forms)
            graph.add((entry_uri, lemon.otherForm, other_form_uri))
            graph.add((other_form_uri, RDF.type, lemon.Form))
            graph.add((other_form_uri, lemon.writtenRep, Literal(morph, lang=context.lang)))
            other_forms += 1

    # Find senses
    if cased_lemma.islower():
        #cursor.execute("select * from senses where wordid=? and casedwordid is NULL", (word_id,))
        cursor.execute("select * from senses where wordid=?", (word_id,))
    else:
        cursor.execute("select casedwordid from casedwords where cased=?",(cased_lemma,))
        row = cursor.fetchone()
        if row is None:
            return None
        casedwordid, = row
        cursor.execute("select * from senses where casedwordid=?", (casedwordid,))
    for _, casedwordid, synsetid, senseid, sensenum, lexid, tagcount, old_sensekey, sensekey in cursor.fetchall():
        # NB. This could also be achieved by querying "casedwordid is NULL" however
        # this is significantly slower, so we filter in Python checking we return cased
        # forms only for cased lemmas
        if cased_lemma.islower() == bool(casedwordid):
            continue
        if sensekey[-1] == pos:
            this_pos_found = True
            _, sensekey2 = sensekey.split('#')
            sense_uri = entry_name(cased_lemma, pos, sensekey2)
            graph.add((entry_uri, lemon.sense, sense_uri))
            graph.add((sense_uri, RDF.type, lemon.LexicalSense))
            graph.add((sense_uri, lemon.reference, synset_name(synsetid, pos)))
            graph.add((sense_uri, wn_ontology.sense_number, Literal(sensenum)))
            graph.add((sense_uri, wn_ontology.tag_count, Literal(tagcount)))
            graph.add((sense_uri, wn_ontology.lex_id, Literal(lexid)))
            graph.add((sense_uri, wn_ontology.old_sense_key, Literal(old_sensekey)))

            # Now adjective positions
            cursor.execute("select position from adjpositions where synsetid=? and wordid=?", (synsetid, word_id))
            rows = cursor.fetchall()
            for position, in rows:
                graph.add((sense_uri, wn_ontology.adjposition,
                           URIRef(wn_ontology.term(quote_plus(context.adjposition_names[position])))))

            # Add definition also to sense
            cursor.execute("select definition from synsets where synsetid=?", (synsetid,))
            for definition, in cursor.fetchall():
                graph.add((sense_uri, wn_ontology.gloss, Literal(definition, lang=context.lang)))

            # Sense links
            cursor.execute("select senseid2, linkid from lexlinks where senseid1=?", (senseid,))
            for senseid2, linkid in cursor.fetchall():
                cursor.execute("select sensekey from senses where senseid=?", (senseid2,))
                sensekey3, = cursor.fetchone()
                sense2_lemma, sense2_key = sensekey3.split('#')
                pos2 = sensekey3[-1]
                sense_uri2 = entry_name(sense2_lemma, pos2, sense2_key)
                graph.add((sense_uri, wn_ontology.term(context.linktypes[linkid]), sense_uri2))

            # Verb frames (maybe only if pos=='v'?)
            cursor.execute("select sentenceid from vframesentencemaps where synsetid=? and wordid=?",
                           (synsetid, word_id))
            for sentenceid, in cursor.fetchall():
                graph.add((sense_uri, wn_ontology.verb_frame_sentence,
                           Literal(context.vframesentences[sentenceid], lang=context.lang)))

            # Sense tags
            cursor.execute("select position, senseid from sensetags inner join taggedtexts on sensetags.sensetagid=taggedtexts.sensetagid where new_sensekey=?",(sensekey,)) # unindexed
            for position, senseid in cursor.fetchall():
                cursor.execute("select sensekey from senses where senseid=?",(senseid,))
                for sensekey, in cursor.fetchall():
                    if position:
                        comp_uri = entry_name(sensekey[0:sensekey.index('#')].replace("_"," "),sensekey[-1],'Component-' + str(position+1))
                        graph.add((sense_uri, wn_ontology.sense_tag, comp_uri))
            
            # LexVo Link
            graph.add((sense_uri, OWL.sameAs, translate_to_lexvo(old_sensekey, pos)))

                 
    if not this_pos_found:
        return None

    if pos == "p":
        words = lemma.split(" ")
        node = BNode()
        comp1 = entry_name(lemma, pos, "Component-1")
        graph.add((entry_uri, lemon.decomposition, node))
        graph.add((node, RDF.first, comp1))
        graph.add((comp1, RDFS.label, Literal(words[0], lang=context.lang)))
        graph.add((comp1, RDF.type, lemon.Component))

        for idx in range(1,len(words)):
            node2 = BNode()
            graph.add((node, RDF.rest, node2))
            node = node2
            comp_uri = entry_name(lemma, pos, "Component-" + str(idx + 1))
            graph.add((node, RDF.first, comp_uri))
            graph.add((comp_uri, RDFS.label, Literal(words[idx], lang=context.lang)))
            graph.add((comp_uri, RDF.type, lemon.Component))
        graph.add((node, RDF.rest, RDF.nil))

    try:
        cursor.execute("select fragment, property, object from entrytriples where lemma=?",(quote_plus(lemma)+"-"+pos,))
        for f, p, o in cursor.fetchall():
            graph.add((entry_name(lemma,pos,f), from_n3(p), from_n3(o)))
    except:
        pass


    return graph


def main(argv=None):
    opts = dict(getopt.getopt(argv[1:],'qd:l:o:')[0])
    context = WNRDFContext(opts.get('-d','wordnet_3.1+.db'))
    context.dump(file=opts.get('-o','wordnet.nt'), verbose=('-q' not in opts), limit=int(opts.get('-l',-1)))


if __name__ == '__main__':
    main(sys.argv)
