# Used to generate ontology.rdf
# Simply run as:
#   python build_ontology.py
# To update ontology.rdf
from WNRDF import *
from rdflib import *
import re

__author__ = 'jmccrae'

isocat = Namespace("http://www.isocat.org/datcat/")
dcr = Namespace("http://www.isocat.org/ns/dcr.rdf#")

context = WNRDFContext("wordnet_3.1+.db")

g = ConjunctiveGraph()

ontology_uri = URIRef(str(ontology_name(""))[0:-1])

cursor = context.conn.cursor()

g.add((ontology_uri, RDF.type, OWL.Ontology))
g.add((ontology_uri, OWL.imports, URIRef("http://www.monnet-project.eu/lemon")))
g.add((dcr.datcat, RDF.type, OWL.AnnotationProperty))

def uncamelcase(label):
    return re.sub("([A-Z])"," \g<0>",label).lstrip() 

def add_class(name,dc=None):
    global g
    g.add((ontology_name(name), RDF.type, OWL.term("Class")))
    g.add((ontology_name(name), RDFS.label, Literal(uncamelcase(name).capitalize(), lang="en")))
    if dc:
        g.add((ontology_name(name), dcr.datcat, isocat.term("DC-%d" % dc)))

def add_oprop(name,parent=None,dc=None):
    global g
    if parent:
        g.add((ontology_name(name),RDFS.subPropertyOf,ontology_name(parent)))
    else:
        g.add((ontology_name(name), RDF.type, OWL.ObjectProperty))
    g.add((ontology_name(name), RDFS.label, Literal(name.replace("_"," ").capitalize(), lang="en")))
    if dc:
        g.add((ontology_name(name), dcr.datcat, isocat.term("DC-%d" % dc)))

def add_dprop(name,dc=None):
    global g
    g.add((ontology_name(name), RDF.type, OWL.DatatypeProperty))
    g.add((ontology_name(name), RDFS.label, Literal(name.replace("_"," ").capitalize(), lang="en")))
    if dc:
        g.add((ontology_name(name), dcr.datcat, isocat.term("DC-%d" % dc)))

def add_ind(name,parent,dc=None):
    global g
    g.add((ontology_name(name), RDF.type, ontology_name(parent)))
    g.add((ontology_name(name), RDFS.label, Literal(name.replace("_"," ").capitalize(), lang="en")))
    if dc:
        g.add((ontology_name(name), dcr.datcat, isocat.term("DC-%d" % dc)))

isocatlinks = {
    "attributive": 5242,
    "predicate": 2710,
    "immediately postnomial": 4619,
    "hypernym": 31,
#hyponym
#instance hypernym
#instance hyponym
    "part meronym": 492,
    "part holonym": 95,
#member holonym
#member meronym
#substance holonym
#substance meronym
    "entails": 205,
    "causes": 2102,
    "antonym": 83,
    "similar": 438,
    "also": 461,
    "attribute": 2267,
#verb group
#participle, maybe 1341?
#pertainym
    "derivation": 4611,
    "domain category": 100,
#domain member category
    "domain region": 243,
#domain member region
    "domain usage": 6147,
#domain member usage
    "noun": 1333,
    "verb": 1424,
    "adjective": 1230,
    "adverb": 1232,
#adjective satellite
    "phrase": 2282,
    "idiom": 351
}

add_class("Synset",dc=4613)

add_class("LexicalDomain")
add_oprop("lexical_domain")
for lexdomainname in context.lexdomainid_to_name.values():
    add_ind(lexdomainname,"LexicalDomain")

add_class("AdjectivePosition")
for adjpositionname in context.adjposition_names.values():
    add_ind(adjpositionname,"AdjectivePosition",isocatlinks.get(adjpositionname))

add_oprop("link")
for link_type in context.linktypes.values():
    add_oprop(link_type,"link",isocatlinks.get(link_type))
    cursor.execute("select recurses from linktypes where link=?",(link_type.replace("_"," "),))
    recurses, = cursor.fetchone()
    if recurses:
        g.add((ontology_name(link_type), RDF.type, OWL.TransitiveProperty))

add_oprop("part of speech", dc=396)
add_class("PartOfSpeech",dc=396)
for pos in context.postypes.values():
    add_ind(pos, "PartOfSpeech", isocatlinks.get(pos))

add_dprop("gloss",dc=244)
add_oprop("synset member")
add_oprop("phrase type")
add_class("PhraseType")

cursor.execute("select distinct phrasetype from phrasetypes")
for phrasetype, in cursor.fetchall():
    add_ind(phrasetype,"PhraseType",isocatlinks.get(phrasetype))

add_dprop("sample",dc=455)
add_dprop("tag count")
add_dprop("sense number")
add_dprop("verb frame sentence")
add_dprop("old sense key")
add_oprop("sense tag")
add_oprop("translation",dc=2970)
add_oprop("verbnet class")

g.serialize("ontology.rdf")
