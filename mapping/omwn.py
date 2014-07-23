# Execute as
#   python omwn.py | python ../WNFromRDF.py | sqlite3 ../wordnet_3.1+.db
import zipfile
import sys
from os.path import exists
import sqlite3

wn_prefix = "http://wordnet.princeton.edu/rdf/"
wn_version = "wn31"

if not exists("all.zip"):
    print "Please download http://compling.hss.ntu.edu.sg/omw/all.zip"
    sys.exit()

langs = { ('als','als'): 'sqi',
        ('arb','arb'): 'ara',
        ('cmn','cmn'): 'zho',
        ('dan','dan'): 'dan',
        ('fas','fas'): 'fas',
        ('fin','fin'): 'fin',
        ('fra','fra'): 'fra',
        ('heb','heb'): 'heb',
        ('ita','ita'): 'ita',
        ('jpn','jpn'): 'jpn',
        ('mcr','cat'): 'cat',
        ('mcr','eus'): 'eus',
        ('mcr','glg'): 'glg',
        ('mcr','spa'): 'spa',
        ('msa','ind'): 'ind',
        ('msa','zsm'): 'zsm',
        ('nor','nno'): 'nno',
        ('nor','nob'): 'nob',
        ('pol','pol'): 'pol',
        ('por','por'): 'por',
        ('tha','tha'): 'tha'
        }

all_zip = zipfile.ZipFile('all.zip')

conn = sqlite3.connect("mapping.db")
cursor = conn.cursor()

for (folder_key, file_key), lang in langs.items():
    tab_file = all_zip.open('wns/%s/wn-data-%s.tab' % (folder_key, file_key))
    for line in tab_file:
        if not line.startswith('#'):
            if len(line.split("\t")) == 3:
                synsetid, prop, obj = line.split("\t")
                if prop.endswith("lemma"):
                    pos = synsetid[-1]
                    cursor.execute("select wn31 from wn31 where wn30=?",(synsetid,))
                    rows = cursor.fetchall()
                    if not rows:
                        sys.stderr.write("Lost id: %s (%s, %s)\n" % (synsetid, lang, obj.strip()))
                    for offset, in rows:
                        print "<%s%s-%d-%s> <%sontology#translation> \"%s\"@%s ." % (wn_prefix, wn_version, offset, pos, wn_prefix, obj.replace("\"","\\\"").strip(), lang)


