import sqlite3
import sys
import re

splits = {
# Splits
'02795978-n': '(102799187-n);102799001-n',
'03794136-n': '(104455013-n);103799669-n',
'00688377-v': '200690278-v;200714537-v',
'02672831-n': '102675461-n;(102675726-n)',
'02713992-n': '(102716929-n);(102716785-n)',
'02672831-n': '102675461-n;(102675726-n)',
'00803432-a': '300807002-s',
'01301051-v': '(201303637-v);(201304044-v)',
'06823760-n': '(106836790-n);106836640-n',
'00202934-v': '(200295646-v);(200203298-v)',
'01301051-v': '201303637-v;(201304044-v)',
'12578255-n': '(112599160-n);112598760-n',
'00845523-n': '100847184-n',
'08963369-n': '(108984077-n);108983142-n',
'00824767-v': '(200825727-v);200826456-v',
'02572119-v': '(202578494-v);202578034-v',
'00046299-r': '(400473918-r);400046739-r',
'01878870-a': '(301885720-s);301884969-s',
'07035153-n': '107048658-n;(107048857-n)',
'00949619-n': '(100951435-n);(100951878-n)',
'10210648-n': '110230249-n;(110230422-n)',
'00766234-n': '(100767587-n);100767761-n',
'00779248-n': '(100781071-n);100780744-n',
'01965512-a': '301972513-s;(301972355-s)',
'10000459-n': '110019979-n;(110020122-n)',
'10002031-n': '110021572-n;(110021663-n)',
'10012484-n': '110032138-n;(110032289-n)',
'09570298-n': '(109593643-n);(109593427-n)',
'01934026-a': '301940682-s;(301940473-s)',
'02275412-a': '302281701-s;(302281587-s)',
'05820462-n': '(105828731-n);105828606-n',
'02436025-a': '(302445314-s);302445119-s',
'00802179-s': '300805871-s',
'00780944-s': '300805750-s',
'08903220-n': 'none',
'00802179-s': '300805871-s',
'00780944-s': '300805750-s',
# Merges
'03696065-n': '103701391-n',
'02873244-n': '103701391-n',
'00429355-a': '300430851-s',
'00429355-a': '300430851-s',
'03013037-a': '303024459-a',
'03012707-a': '303024459-a',
'00897746-v': '200899241-v',
'00784342-v': '200899241-v',
'07294907-n': '107309129-n',
'07294423-n': '107309129-n',
'02092907-v': '202097174-v',
'02010255-v': '202097174-v',
'08153022-n': '108102739-n',
'08085824-n': '108102739-n',
'00767349-a': '300766556-s',
'00768098-a': '300766556-s',
'02980583-a': '302914135-a',
'02902883-a': '302914135-a',
'00712708-v': '200714537-v',
'00688377-v': '200714537-v',
'03696065-n': '103701391-n',
'02873244-n': '103701391-n',
'00712708-v': '200714537-v',
'00688377-v': '200714537-v',
'00205125-r': '400008423-r',
'00008007-r': '400008423-r',
'03696065-n': '103701391-n',
'02873244-n': '103701391-n',
'07968974-n': '107985266-n',
'08375526-n': '107985266-n',
'00471613-n': '100472688-n',
'00474568-n': '100472688-n',
'09637013-n': '109659490-n',
'09636339-n': '109659490-n',
'00166875-r': '400086161-r',
'00085811-r': '400086161-r',
'00079866-r': '400080132-r',
'00258282-r': '400080132-r',
'00471613-n': '100472688-n',
'00474568-n': '100472688-n',
'00502325-r': '400386914-r',
'00385081-r': '400386914-r',
'10621140-n': '110172934-n',
'10153414-n': '110172934-n',
'00064691-r': '400172866-r',
'00171457-r': '400172866-r',
'00847861-a': '300851098-s',
'00847577-a': '300851098-s',
'00112279-r': '400113022-r',
'00128882-r': '400113022-r',
'00712708-v': '200714537-v',
'00688377-v': '200714537-v',
'00242575-a': '300244035-s',
'00242832-a': '300244035-s',

'01301410-v': '201304044-v',
'00767349-a': '300766556-s',
'00294884-v': '200295646-v',
'09570522-n': '109593643-n',
'02024928-a': '302032205-s',
'08903049-n': '108923207-n',
'00086005-a': '300086690-s',
'01085268-a': '301088956-s',
'00471945-r': '400473918-r',
'02273838-a': '302281587-s',
'01879667-a': '301885720-s',
'08964647-n': '108984077-n',
'00824066-v': '200825727-v',
'02064127-a': '302071531-s',
'01230965-n': '101233454-n',
'00763407-a': '300766950-s',
'00990855-a': '300994085-s',
'00990192-a': '300993331-s',
# Other mappings
'01301051-v': '201303637-v',
'00431774-a': '300433489-s',
'00431774-a': '300433489-s',
'00768098-a': '300771658-s',
'00768098-a': '300771658-s',
'00202934-v': '200203298-v',
'09570298-n': '109593427-n',
'00768397-a': '300771957-s',
'00845523-n': '100847184-n',
'02068946-a': '302076350-s',
'00824767-v': '200826456-v',
'08963369-n': '108983142-n',
'01878870-a': '301884969-s',
'02275412-a': '302283161-s',
'00046299-r': '400046739-r',
'01457692-a': '301460500-s',
'00088055-a': '300088740-s',
'02025274-a': '302032677-s',
'02415025-a': '302423821-s',
'00988988-a': '300992194-s',
'00040058-a': '300040189-s',
'00816839-a': '300820408-s',
'01063102-a': '301066791-s',
'01068306-a': '301072013-s',
'01447937-a': '301450828-s',
'02105603-a': '302112883-s'
}

def fix_sensekey(sensekey):
    if re.match("\d+",sensekey[-2:]):
        return sensekey[:-2]
    else:
        return sensekey

def read_wn31_sensekeys():
    wn31i_sensekeys = dict()
    wn31r_sensekeys = dict()
    conn1 = sqlite3.connect("../wordnet_3.1+.db")
    cursor1 = conn1.cursor()
    cursor1.execute("select old_sensekey, senses.synsetid, pos from senses join synsets on senses.synsetid = synsets.synsetid")
    conn2 = sqlite3.connect("mapping.db")
    cursor2 = conn2.cursor()
    for old_sensekey, synsetid, pos in cursor1.fetchall():
        old_sensekey = fix_sensekey(old_sensekey)
        wn31i_sensekeys[old_sensekey] = "%d-%s" % (synsetid, pos)
        cursor2.execute("select release from wn31r where internal=?", (synsetid,))
        row = cursor2.fetchone()
        if row:
            release, = row
            wn31r_sensekeys[old_sensekey] = "%d-%s" % (release, pos)
        #else:
        #    sys.stderr.write("No release key for %d\n" % synsetid)
    return (wn31i_sensekeys, wn31r_sensekeys)

def read_wn30_sensekeys():
    wn30_sensekeys = dict()
    for line in open("wn30-senses.csv"):
        sensekey, synsetid = line.strip().split(",")
        wn30_sensekeys[fix_sensekey(sensekey)] = synsetid
    return wn30_sensekeys

if __name__ == "__main__":
    #print("\"sensekey\",\"wn30\",\"wn31i\",\"wn31r\"")
    #print("\"wn31\",\"wn30_1\",\"wn30_2\",\"sensekey_1\",\"sensekey_2\"")
    #print("\"wn30\",\"wn31_1\",\"wn31_2\",\"sensekey_1\",\"sensekey_2\"")
    print("\"wn30\",\"wn31\"")
    (wn31i_sensekeys, wn31r_sensekeys) = read_wn31_sensekeys()
    wn30_sensekeys = read_wn30_sensekeys()
#    wn31r2wn30 = dict()
#    f = open("wn30-31.csv","w")
    for sensekey, synsetid in wn30_sensekeys.items():
        if sensekey in wn31i_sensekeys:
            wn31i_synset = wn31i_sensekeys[sensekey]
        else:
            wn31i_synset = ""
        if sensekey in wn31r_sensekeys:
            wn31r_synset = wn31r_sensekeys[sensekey]
        else:
            wn31r_synset = ""
        if wn31r_synset != "" and synsetid not in splits:
            print("%s,%s" % (synsetid, wn31r_synset))
    for a,b in splits.items():
        print("%s,%s" % (a,b))

    for line in open("wn30-31-verified.csv"):
        print(line.strip())
        #print("%s,%s,%s,%s" % (sensekey, synsetid, wn31i_synset, wn31r_synset))
#        if wn31r_synset != "" and wn31r_synset in wn31r2wn30:
#            other_synsetid,other_sensekey = wn31r2wn30[wn31r_synset]
#            if synsetid != other_synsetid and synsetid not in ignores and other_synsetid not in ignores:
#                print("%s,%s,%s,%s,%s" % (wn31r_synset, synsetid, other_synsetid, sensekey, other_sensekey))
#        elif wn31r_synset != "":
#            wn31r2wn30[wn31r_synset] = (synsetid,sensekey)
#    wn302wn31r = dict()
#    for sensekey, synsetid in wn31r_sensekeys.items():
#        if sensekey in wn30_sensekeys:
#            wn30_synset = wn30_sensekeys[sensekey]
#            if wn30_synset in wn302wn31r:
#                other_synsetid, other_sensekey = wn302wn31r[wn30_synset]
#                if synsetid != other_synsetid:
#                     print("%s,%s,%s,%s,%s" % (wn30_synset, synsetid, other_synsetid, sensekey, other_sensekey))
#            else:
#                wn302wn31r[wn30_synset] = (synsetid,sensekey)
#                    







