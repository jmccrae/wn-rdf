import re
import os
import sys
sys.path.append(os.path.dirname(__file__))
import WNRDF
import lxml.etree as et
from cStringIO import StringIO
from wsgiref.simple_server import make_server
from urlparse import parse_qs
from urllib import unquote_plus
from rdflib import RDFS, URIRef, Graph
from rdflib import plugin
from rdflib.store import Store, VALID_STORE
import multiprocessing
import getopt
import time
from os.path import exists
import sqlite3
import cgi

__author__ = 'jmccrae'


class SPARQLExecutor(multiprocessing.Process):
    def __init__(self, query, mime_type, default_graph_uri, pipe, graph):
        multiprocessing.Process.__init__(self)
        self.result = None
        self.result_type = None
        self.query = str(query)
        if mime_type == "html" or mime_type == "json-ld":
            self.mime_type = "pretty-xml"
        else:
            self.mime_type = mime_type
        self.default_graph_uri = default_graph_uri
        self.pipe = pipe
        self.graph = graph


    def run(self):
        t1 = time.time()
        print("Starting: %s" % self.query)
        try:
            qres = self.graph.query(self.query, initNs=self.default_graph_uri)
            print("Query completed in %f seconds" % (time.time() - t1))
        except Exception as e:
            print(e)
            self.pipe.send(('error','Bad query'))
            return
        if qres.type == "CONSTRUCT" or qres.type == "DESCRIBE":                
            self.pipe.send((self.mime_type, qres.serialize(format=self.mime_type)))
        else:
            self.pipe.send(('sparql', qres.serialize()))


def resolve(fname):
    if os.path.dirname(__file__):
        return os.path.dirname(__file__) + "/" + fname
    else:
        return fname
     

class WNRDFServer:
    def __init__(self, db, mapping_db):
        self.mime_types = dict(
            [('html', 'text/html'), ('pretty-xml', 'application/rdf+xml'), ('turtle', 'text/turtle'),
             ('nt', 'text/plain'), ('json-ld', 'application/json'), ('sparql', 'application/sparql-results+xml'
                 )])
        self.wordnet_context = WNRDF.WNRDFContext(db, mapping_db)
        self.header = open(resolve("header")).read()
        self.footer = open(resolve("footer")).read()


    @staticmethod
    def send302(start_response, location):
        start_response('302 Found', [('Location', location)])
        return ['Moved to ' + location]
       
    @staticmethod
    def send400(start_response):
        start_response('400 Bad Request', [('Content-type', 'text/plain')])
        return ['Invalid SPARQL query']

    @staticmethod
    def send404(start_response):
        start_response('404 Not Found', [('Content-type', 'text/plain')])
        return ['Page not found']

    @staticmethod
    def send501(start_response):
        start_response('501 Not Implemented', [('Content-type', 'text/plain')])
        return ['You requested a format not installed on this server']

    def render_html(self, title, text):
        html = self.header.replace("%%TITLE%%",title) + text + self.footer
        return html

    @staticmethod
    def best_mime_type(accept_string):
        accepts = re.split("\s*,\s*", accept_string)
        for accept in accepts:
            if accept == "text/html":
                return "html"
            elif accept == "application/rdf+xml":
                return "pretty-xml"
            elif accept == "text/turtle" or accept == "application/x-turtle":
                return "turtle"
            elif accept == "application/n-triples" or accept == "text/plain":
                return "nt"
            elif accept == "application/json":
                return "json-ld"
            elif accept == "application/sparql-results+xml":
                return "sparql"
        best_q = -1
        best_mime = "html"
        for accept in accepts:
            if ";" in accept:
                mime = re.split("\s*;\s*", accept)[0]
                extensions = re.split("\s*;\s*", accept)[1:]
                for extension in extensions:
                    if "=" in extension and re.split("\s*=\s*", extension)[0] == "q":
                        try:
                            q = float(re.split("\s*=\s*", extension)[1])
                        except:
                            continue
                        if q > best_q:
                            if mime == "text/html":
                                best_q = q
                                best_mime = "html"
                            if mime == "application/rdf+xml":
                                best_q = q
                                best_mime = "pretty-xml"
                            if mime == "text/turtle" or mime == "application/x-turtle":
                                best_q = q
                                best_mime = "turtle"
                            if mime == "application/n-triples" or mime == "text/plain":
                                best_q = q
                                best_mime = "nt"
                            if mime == "application/json":
                                best_q = q
                                best_mime = "json-ld"
                            if mime == "application/sparql-results+xml":
                                best_q = q
                                best_mime = "sparql"
        return best_mime

    
    def sparql_query(self, query, mime_type, default_graph_uri, start_response, timeout=10):
        try:
            store = plugin.get('Sleepycat', Store)(resolve("store"))
            identifier = URIRef(WNRDF.prefix[:-1])
            try:
                graph = Graph(store, identifier=identifier)
                parent, child = multiprocessing.Pipe()
                executor = SPARQLExecutor(query, mime_type, default_graph_uri, child, graph)
                executor.start()
                executor.join(timeout)
                if executor.is_alive():
                    start_response('503 Service Unavailable', [('Content-type','text/plain')])
                    executor.terminate()
                    return "The query could not be processed in time"
                else:
                    result_type, result = parent.recv()
                    if result_type == "error":
                        return self.send400(start_response)
                    elif mime_type != "html" or result_type != "sparql":
                        start_response('200 OK', [('Content-type',self.mime_types[result_type])])
                        return [str(result)]
                    else:
                        start_response('200 OK', [('Content-type','text/html')])
                        dom = et.parse(StringIO(result))
                        xslt = et.parse(resolve("sparql2html.xsl"))
                        transform = et.XSLT(xslt)
                        newdom = transform(dom)
                        return self.render_html("SPARQL Results", et.tostring(newdom, pretty_print=True)) 
            finally:
                if graph:
                    graph.close()
        finally:
            if store:
                store.close()


    def rdfxml_to_html(self, graph, title=""):
        dom = et.parse(StringIO(graph.serialize(format="pretty-xml")))
        xslt = et.parse(resolve("rdf2html.xsl"))
        transform = et.XSLT(xslt)
        newdom = transform(dom)
        return self.render_html(title, et.tostring(newdom, pretty_print=True))

    def application(self, environ, start_response):
        uri = environ['PATH_INFO']
        if re.match(".*\.html", uri):
            mime = "html"
        elif re.match(".*\.rdf", uri):
            mime = "pretty-xml"
        elif re.match(".*\.ttl", uri):
            mime = "turtle"
        elif re.match(".*\.nt", uri):
            mime = "nt"
        elif re.match(".*\.json", uri):
            mime = "json-ld"
        elif 'HTTP_ACCEPT' in environ:
            mime = self.best_mime_type(environ['HTTP_ACCEPT'])
        else:
            mime = "html"

        if uri == "/" or uri == "/index.html":
            start_response('200 OK', [('Content-type', 'text/html')])
            return [self.render_html("WordNet RDF",open(resolve("index.html")).read())]
        if uri == "/license.html":
            start_response('200 OK', [('Content-type', 'text/html')])
            return [self.render_html("WordNet RDF",open(resolve("license.html")).read())]
        elif uri == "/wnrdf.css" or uri == "/sparql/wnrdf.css":
            start_response('200 OK', [('Content-type', 'text/css')])
            return [open(resolve("wnrdf.css")).read()]
        elif re.match("/%s/(\d+)\-[nvarspNVARSP](|\.nt|\.html|\.rdf|\.ttl|\.json)$" % WNRDF.wn_version, uri):
            synset_id = re.findall("/%s/(\d+)\-[nvarspNVARSP]" % WNRDF.wn_version, uri)[0]
            if len(synset_id) == 8:
                synset_id = str(WNRDF.pos2number(uri[-1])) + synset_id
                return self.send302(start_response,"/%s/%s-%s" % (WNRDF.wn_version, synset_id, uri[-1]))
            translate = True
            if synset_id[-1].isupper():
                synset_id[-1] = synset_id[-1].lower()
                translate = False
            graph = WNRDF.synset(self.wordnet_context, int(synset_id), extras=mime == "html", translate=translate)
            if graph is None:
                return self.send404(start_response)
            title = ', '.join(sorted([str(o) for _, _, o in graph.triples((None, RDFS.label, None))]))
            if mime == "html":
                content = self.rdfxml_to_html(graph, title)
            else:
                try:
                    content = graph.serialize(format=mime, context=self.wordnet_context.jsonld_context)
                except Exception:
                    return self.send501(start_response)
            start_response('200 OK', [('Content-type', self.mime_types[mime]),('Vary','Accept'), ('Content-length', str(len(content)))])
            return [content]
#        elif re.match("/title/%s/(\d+)\-[nvarsp](|\.nt|\.html|\.rdf|\.ttl|\.json)$" % WNRDF.wn_version, uri):
#            synset_id = re.findall("/%s\-(\d+)\-[nvarsp]" % WNRDF.wn_version, uri)[0]
#            graph = WNRDF.synset(self.wordnet_context, int(synset_id))
#            if graph is None:
#                return self.send404(start_response)
#            title = ', '.join(sorted([str(o) for _, _, o in graph.triples((None, RDFS.label, None))])) 
#            start_response('200 OK', [('Content-type', 'text/plain')])
#            return [title]
        elif re.match("/%s/(.*)\-[nvarsp](|\.nt|\.html|\.rdf|\.ttl|\.json)$" % WNRDF.wn_version, uri):
            lemma_pos, = re.findall("^/%s/(.*)\-([nvarsp])" % WNRDF.wn_version, uri)
            lemma, pos = lemma_pos
            graph = WNRDF.entry(self.wordnet_context, unquote_plus(lemma), pos)
            if graph is None:
                return self.send404(start_response)
            can_form = graph.value(WNRDF.entry_name(unquote_plus(lemma), pos), WNRDF.lemon.canonicalForm)
            title = graph.value(can_form, WNRDF.lemon.writtenRep)
            if mime == "html":
                content = self.rdfxml_to_html(graph, str(title))
            else:
                try:
                    content = graph.serialize(format=mime, context=self.wordnet_context.jsonld_context,
                                              base=WNRDF.entry_name(unquote_plus(lemma), pos))
                except Exception as x:
                    return self.send501(start_response)
            start_response('200 OK', [('Content-type', self.mime_types[mime]),('Vary','Accept'), ('Content-length', str(len(content)))])
            return [content]
        elif re.match("/wn30/(\d{8}\-[nvarsp])(|\.nt|\.html|\.rdf|\.ttl|\.json)$", uri):
            (synset_id, ext), = re.findall("/wn30/(\d{8}\-[nvarsp])(|\.nt|\.html|\.rdf|\.ttl|\.json)$", uri)
            with sqlite3.connect(resolve('mapping/mapping.db')) as conn:
                c = conn.cursor()
                c.execute("select wn31 from wn30 where wn30=?", (synset_id,))
                row = c.fetchone()
                if row:
                    wn31, = row
                    return self.send302(start_response, "/wn31/%s-%s" % (wn31, synset_id[-1]))
                else:
                    return self.send404(start_response)
        elif re.match("/wn20/(\d{8}\-[nvarsp])(|\.nt|\.html|\.rdf|\.ttl|\.json)$", uri):
            (synset_id, ext), = re.findall("/wn20/(\d{8}\-[nvarsp])(|\.nt|\.html|\.rdf|\.ttl|\.json)$", uri)
            print(synset_id)
            with sqlite3.connect(resolve('mapping/mapping.db')) as conn:
                c = conn.cursor()
                c.execute("select wn31 from wn30 join wn20 on wn30.wn30 = wn20.wn30 where wn20=?", (synset_id,))
                row = c.fetchone()
                if row:
                    wn31, = row
                    return self.send302(start_response, "/wn31/%s-%s" % (wn31, synset_id[-1]))
                else:
                    return self.send404(start_response)
        elif uri == "/search":
            start_response('200 OK', [('Content-type', 'text/html')])
            if 'QUERY_STRING' in environ:
                qs_parsed = parse_qs(environ['QUERY_STRING'])
                if 'query' in qs_parsed:
                    lemma = qs_parsed['query'][0]
                    result = self.search(self.wordnet_context, lemma)
                    return [result]
                else:
                    return ["No query"]
            else:
                return ["No query string"]
        elif uri == "/ontology":
            start_response('200 OK', [('Content-type', 'application/rdf+xml'),
                                      ('Content-length', str(os.stat("ontology.rdf").st_size))])
            return [open(resolve("ontology.rdf")).read()]
        elif uri == ("/%s.nt.gz" % WNRDF.wn_version):
            start_response('200 OK', [('Content-type', 'appliction/x-gzip'),
                                      ('Content-length', str(os.stat("wordnet.nt.gz").st_size))])
            return open(resolve("wordnet.nt.gz"), "rb").read()
        elif uri.startswith("/flag/") and exists(resolve(uri[1:])):
            start_response('200 OK', [('Content-type', 'image/gif'),
                ('Content-length', str(os.stat(resolve(uri[1:])).st_size))])
            return open(resolve(uri[1:]), "rb").read() 
        elif uri == "/sparql/":
            if 'QUERY_STRING' in environ:
                qs = parse_qs(environ['QUERY_STRING'])
                if 'query' in qs:
                    return self.sparql_query(qs['query'][0], mime, qs.get('default-graph-uri',[None])[0], start_response)
                else:
                    start_response('200 OK', [('Content-type', 'text/html')])
                    return [self.render_html("WordNet RDF",open(resolve("sparql.html")).read())]
            else:
                start_response('200 OK', [('Content-type', 'text/html')])
                return [self.render_html("WordNet RDF",open(resolve("sparql.html")).read())]
        else:
            return self.send404(start_response)

    # From http://hetland.org/coding/python/levenshtein.py
    @staticmethod
    def levenshtein(a, b):
        "Calculates the Levenshtein distance between a and b."
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n

        current = range(n + 1)
        for i in range(1, m + 1):
            previous, current = current, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete = previous[j] + 1, current[j - 1] + 1
                change = previous[j - 1]
                if a[j - 1] != b[i - 1]:
                    change = change + 1
                current[j] = min(add, delete, change)

        return current[n]

    def build_search_table(self, values_sorted, cursor, mc):
        last_lemma = ""
        last_pos = ""
        for lemma, pos, synsetid, definition in values_sorted:
            mc.execute("select release from wn31r where internal=?", (synsetid,))
            r = mc.fetchone()
            if r:
                synsetid2, = r
            else:
                synsetid2 = synsetid
                pos = pos.upper()
            if not lemma == last_lemma or not pos == last_pos:
                last_lemma = lemma
                last_pos = pos
                yield "<tr class='rdf_search_full'><td><a href='%s/%s-%s'>%s</a> (%s)</td><td><a href='%s/%s-%s'>%s</a> &mdash; <span class='definition'>%s</span></td></tr>" % \
                      (WNRDF.wn_version, lemma, pos, lemma, pos, WNRDF.wn_version, synsetid2, pos, self.synset_label(cursor, synsetid), definition)
            else:
                yield "<tr class='rdf_search_empty'><td></td><td><a href='%s/%s-%s'>%s</a> &mdash; <span class='definition'>%s</span></td></tr>" % \
                      (WNRDF.wn_version, synsetid2, pos, self.synset_label(cursor, synsetid), definition)

    @staticmethod
    def synset_label(cursor, offset):
        cursor.execute("select lemma from senses inner join words on words.wordid = senses.wordid where synsetid=?",
                       (offset,))
        return ', '.join([str(lemma) for lemma, in cursor.fetchall()])

    def search(self, context, query_lemma):
        cursor = context.conn.cursor()
        try:
            cursor.execute(
                "select sensekey,senses.synsetid,lemma,definition from words inner join senses, synsets on senses.wordid=words.wordid and senses.synsetid = synsets.synsetid "
                "where soundex(lemma) = soundex(?)",
                (query_lemma,))
        except: # Only if no soundex
            print ("Soundex not supported, please install a newer version of SQLite")
            cursor.execute(
                "select sensekey,senses.synsetid,lemma,definition from words inner join senses, synsets on senses.wordid=words.wordid and senses.synsetid = synsets.synsetid "
                "where lemma = ?",
                (query_lemma,))
        values = [(str(lemma), str(sensekey[-1]), str(synsetid), str(description)) for sensekey, synsetid, lemma, description in cursor.fetchall()]
        mc = context.mconn.cursor()
        if values:
            values_sorted = sorted(values, key=lambda s: self.levenshtein(s[0], query_lemma))[0:49]
            html = "".join(self.build_search_table(values_sorted, cursor, mc))
            return self.render_html("Search results", "<h1>Search results</h1> <table class='rdf_search'><thead><tr><th>Word</th><th>Synset</th></tr></thead>"
                                + html + "</table>")
        else:
            return self.render_html("Search results", "<h1>Search results</h1> <p>Nothing found for <b>%s</b></p>" % cgi.escape(query_lemma))


def application(environ, start_response):
    server = WNRDFServer(resolve('wordnet_3.1+.db'), resolve('mapping/mapping.db'))
    return server.application(environ, start_response)

if __name__ == "__main__":
    opts = dict(getopt.getopt(sys.argv[1:],'qd:p:')[0])
    server = WNRDFServer(opts.get('-d','wordnet_3.1+.db'), opts.get('-m','mapping/mapping.db'))
    
    httpd = make_server('localhost', int(opts.get('-p',8051)), server.application)

    while True:
        httpd.handle_request()
