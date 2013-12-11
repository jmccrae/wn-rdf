__author__ = 'jmccrae'

import unittest
import sqlite3
import WNRDF


class MyTestCase(unittest.TestCase):
    def test_synset(self):
        context = WNRDF.WNRDFContext("wordnet_3.1+.db")
        graph = WNRDF.synset(context, 100001740)
        print graph.serialize()
        assert(graph)

    def test_entry(self):
        context = WNRDF.WNRDFContext("wordnet_3.1+.db")
        graph = WNRDF.entry(context, "cat","n")
        print graph.serialize()
        assert(graph)

    def test_adjposition(self):
        context = WNRDF.WNRDFContext("wordnet_3.1+.db")
        graph = WNRDF.entry(context, "inclined","a")
        serialization = graph.serialize()
        assert("adjposition" in serialization)

    #def test_cased(self):
    #    context = WNRDF.WNRDFContext("wordnet_3.1+.db")
    #    graph = WNRDF.entry(context, "'s gravenhage","n")
    #    serialization = graph.serialize()
    #    assert("'s Gravenhage" in serialization)

    def test_morphs(self):
        context = WNRDF.WNRDFContext("wordnet_3.1+.db")
        graph = WNRDF.entry(context, "abhor","v")
        serialization = graph.serialize()
        assert("abhorred" in serialization)
        assert("abhorring" in serialization)

    def test_fail(self):
        context = WNRDF.WNRDFContext("wordnet_3.1+.db")
        graph = WNRDF.synset(context, 0)
        assert(graph is None)

    def test_sample(self):
        context = WNRDF.WNRDFContext("wordnet_3.1+.db")
        graph = WNRDF.synset(context, 100003993)
        serialization = graph.serialize()
        assert("American shopkeeper" in serialization)





if __name__ == '__main__':
    unittest.main()
