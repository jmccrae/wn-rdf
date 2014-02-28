from rdflib import *
from rdflib import plugin
from rdflib.store import Store, NO_STORE, VALID_STORE
import os
import os.path
import sys

if __name__ == "__main__":
    identifier = URIRef("http://wordnet-rdf.princeton.edu/")
    store = plugin.get('Sleepycat', Store)(sys.argv[1])
    path = os.getcwd() + "/" + sys.argv[1]
    assert store.open(sys.argv[1], create=True) == VALID_STORE
    graph = Graph(store, identifier=identifier)
    graph.parse(sys.stdin, format="nt")
    graph.commit()
    print len(graph)
    graph.close()
    assert store.open(sys.argv[1], create=False) == VALID_STORE
    g2 = Graph(store, identifier=identifier)
    print len(g2)
