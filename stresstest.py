import multiprocessing
import sqlite3
import time
import urllib

def do_query(uri):
    t1 = time.time()
    try:
        for line in urllib.urlopen(uri):
            pass
        print "Got %s in %f" % (uri, time.time() - t1)
    except Exception as e:
        print "Failed on %s: %s" % (uri, str(e))


if __name__ == "__main__":
    conn = sqlite3.connect("wordnet_3.1+.db")
    cursor = conn.cursor()
    uris = []
    cursor.execute("select synsetid, wordid, casedwordid from senses order by random() limit 100")
    for synsetid, wordid, casedwordid in cursor.fetchall():
        cursor.execute("select pos from synsets where synsetid=?",(synsetid,))
        pos, = cursor.fetchone()
        if casedwordid:
            cursor.execute("select cased from casedwords where casedwordid=?", (casedwordid,))
            word, = cursor.fetchone()
        else:
            cursor.execute("select lemma from words where wordid=?", (wordid,))
            word, = cursor.fetchone()
        uris += ["http://localhost:8051/wn31-%09d-%s" % (synsetid, pos)]
        uris += ["http://localhost:8051/%s-%s" % (word, pos)]
    print "Starting to query"
    pool = multiprocessing.Pool(20)
    pool.map(do_query, uris)

