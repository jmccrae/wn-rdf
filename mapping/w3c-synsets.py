# Usage
#   python w3c-synsets.py | python ../WNFromRDF.py | sqlite3 ../wordnet_3.1+.db
import sys
import sqlite3

conn = sqlite3.connect("mapping.db")
cursor = conn.cursor()

cursor.execute("select wn31, w3c, wn30.wn30 from w3c join wn20, wn30 on w3c.wn20 = wn20.wn20 and wn20.wn30 = wn30.wn30")

for row in cursor.fetchall():
    wn31, w3c, wn30 = row
    pos = wn30[-1]
    print("<http://wordnet.princeton.edu/rdf/wn31-%09d-%s> <http://www.w3.org/2002/07/owl#sameAs> %s . " % (wn31, pos, w3c))
