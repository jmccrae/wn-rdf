# Usage:
#   python vn.py | python ../WNFromRDF.py | sqlite3 ../wordnet_3.1+.db
import tarfile
from os.path import exists
from urllib import quote_plus
import xml.etree.ElementTree as ET
import sqlite3

wn_prefix = "http://wordnet.princeton.edu/rdf/"
wn_version = "wn31"
vn_prefix = "http://verbs.colorado.edu/verb-index/vn/"

if not exists('verbnet-3.2.tar.gz'):
    print "Please download http://verbs.colorado.edu/verb-index/vn/verbnet-3.2.tar.gz"
    sys.exit()

conn = sqlite3.connect("../wordnet_3.1+.db")
cursor = conn.cursor()
tar = tarfile.open("verbnet-3.2.tar.gz", "r:gz")
for tarinfo in tar:
    if tarinfo.isreg() and tarinfo.name.endswith(".xml"):
        xml = ET.parse(tar.extractfile(tarinfo))
        vn_id = xml.getroot().attrib['ID']
        for member in xml.getroot()[0]:
            wns = member.attrib['wn']
            word = member.attrib['name']
            if wns:
                for wn in wns.split():
                    cursor.execute("select sensekey from senses where old_sensekey=?",(wn+ "::",))
                    for sensekey, in cursor.fetchall():
                        lemma, senseid = sensekey.split('#')
                        pos = senseid[-1]
                        print "<%s%s-%s#%s> <%sontology#verbnet_class> <%s%s.php#%s> ." % (wn_prefix, quote_plus(lemma), pos, senseid.replace(':','-'), wn_prefix, vn_prefix, vn_id, word)
tar.close()
cursor.close()
conn.close()
