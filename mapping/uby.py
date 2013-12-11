# Usage:
#   zcat wn.nt.gz | grep externalReference | python mapping/uby.py | python WNFromRDF.py | sqlite3 wordnet_3.1+.db
import sqlite3
from urllib import quote_plus
import sys

prefix = "http://wordnet.princeton.edu/rdf/"
wn_version = "wn31"

conn = sqlite3.connect("wordnet_3.1+.db")
cursor = conn.cursor()
conn2 = sqlite3.connect("mapping/mapping.db")
cursor2 = conn2.cursor()

pos_string = {
        "noun]" : "n",
        "verb]" : "v",
        "adjective]" : "a",
        "adverb]": "r"
        }


for line in sys.stdin:
    subj, _, obj1, obj2, obj3, _ = line.strip().split()
    if "Sense" in subj:
        sensekey = obj3[:-1]
        cursor.execute("select casedwordid, sensekey from senses where old_sensekey=?", (sensekey,))
        row = cursor.fetchone()
        if row:
            casedwordid, new_sensekey = row
            lemma, frag = new_sensekey.split("#")
            if casedwordid:
                cursor.execute("select cased from casedwords where casedwordid=?",(casedwordid,))
                lemma, = cursor.fetchone()
            print "<%s%s-%s#%s> <http://www.w3.org/2002/07/owl#sameAs> %s> ." % (prefix, quote_plus(lemma), frag[-1], frag.replace(":","-"), subj[:subj.index('#')]) 
        else:
            sys.stderr.write("Lost id: %s\n" % subj)
    elif "Synset" in subj:
        pos = pos_string[obj2] 
        synsetid = "%08d-%s" % ( int(obj3[:-1]), pos)
        cursor2.execute("select wn31 from wn30 where wn30=?",(synsetid,))
        row = cursor2.fetchone()
        if row:
            wn31, = row
            print "<%s%s-%08d-%s> <http://www.w3.org/2002/07/owl#sameAs> %s> ." % (prefix, wn_version, int(wn31), pos, subj[:subj.index('#')])
        elif pos == "a":
            pos = "s" 
            synsetid = "%08d-%s" % (int(obj3[:-1]), pos)
            cursor2.execute("select wn31 from wn30 where wn30=?",(synsetid,))
            row = cursor2.fetchone()
            if row:
                wn31, = row
                print "<%s%s-%08d-%s> <http://www.w3.org/2002/07/owl#sameAs> %s> ." % (prefix, wn_version, int(wn31), pos, subj[:subj.index('#')])
            else:
                sys.stderr.write("Lost id: %s\n" % subj)
        else:
            sys.stderr.write("Lost id: %s\n" % subj)


            


