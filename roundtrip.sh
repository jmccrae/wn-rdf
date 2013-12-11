#!/bin/bash
# This script dumps the data to RDF and then reloads it into
# a new SQLite database at wordnet-rt.db
# Should be used only for verification purposes, of course :)

rm -f wordnet-rt.db
python WNRDF.py -l 100
echo "Loading schema"
bash write_sql_schema.sh | sqlite3 -echo wordnet-rt.db
echo "Loading data"
python WNFromRDF.py -h < wordnet.nt | sqlite3 -echo wordnet-rt.db

