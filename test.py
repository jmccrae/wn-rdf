from rdflib import *

g = Graph()

print(g.parse("example.json", format="json-ld").serialize(format="nt"))
