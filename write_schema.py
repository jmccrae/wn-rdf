## The purpose of this file is to generate the schema from the database
## Thus we can convert from RDF without having to assign new codes for link types, etc.
## It is expected that this file should be run as
##    python write_schema.py > wn_schema.py
import sqlite3

conn = sqlite3.connect("wordnet_3.1+.db")
cursor = conn.cursor()

cursor.execute("select * from lexdomains")
print "# This file is automatically generated by write_schema.py"
print "# Do not edit"

print "lexdomains = {"
print ",\n".join(["  '%s': (%d,'%s')" % (b,a,c) for a,b,c in cursor.fetchall()])
print "}"

cursor.execute("select * from adjpositiontypes")
print "adjpositiontypes = {"
print ",\n".join(["  '%s': '%s'" % (b,a) for a,b in cursor.fetchall()])
print "}"

cursor.execute("select * from linktypes")
print "linktypes = {"
print ",\n".join(["  '%s': (%d,%d,'%s')" % (b,a,c,d) for a,b,c,d in cursor.fetchall()])
print "}"

cursor.execute("select * from postypes")
print "postypes = {"
print ",\n".join(["  '%s': '%s'" % (b,a) for a,b in cursor.fetchall()])
print "}"

cursor.execute("select * from vframesentences")
print "vframesentences = {"
print ",\n".join(["  '%s': %d" % (b.replace("'","\\'"),a) for a,b in cursor.fetchall()])
print "}"

    
cursor.close()
conn.close()