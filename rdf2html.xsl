<?xml version="1.0"?>

<!DOCTYPE xsl:stylesheet [
        <!ENTITY lemon   "http://lemon-model.net/lemon#">
        <!ENTITY wordnet-ontology   "http://wordnet-rdf.princeton.edu/ontology#">
        <!ENTITY wordnet "http://wordnet-rdf.princeton.edu/wn31/">
        <!ENTITY rdf   "http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <!ENTITY rdfs   "http://www.w3.org/2000/01/rdf-schema#">
        <!ENTITY verbnet "http://verbs.colorado.edu/verb-index/vn/">
        <!ENTITY lexvo "http://www.lexvo.org/page/iso639-3/">
        <!ENTITY owl "http://www.w3.org/2002/07/owl#">
        <!ENTITY lemonUby "http://lemon-model.net/lexica/uby/wn/">
        <!ENTITY w3c-wn "http://www.w3.org/2006/03/wn/wn20/instances/">
        <!ENTITY lexvo-wn "http://www.lexvo.org/page/wordnet/30/">
        ]>

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
                xmlns:lemon="http://lemon-model.net/lemon#"
                xmlns:wordnet-ontology="http://wordnet-rdf.princeton.edu/ontology#"
        >

    <xsl:template match="/rdf:RDF">
        <span>
            <xsl:attribute name="resource">
            <xsl:choose>
                <xsl:when test="lemon:LexicalEntry">
                    <xsl:value-of select="lemon:LexicalEntry/@rdf:about"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="wordnet-ontology:Synset/@rdf:about"/>
                </xsl:otherwise>
            </xsl:choose>
            </xsl:attribute>
            <a property="&rdf;type" style="display:none;">
            <xsl:attribute name="href">
                <xsl:choose>
                    <xsl:when test="lemon:LexicalEntry">&lemon;LexicalEntry</xsl:when>
                    <xsl:otherwise>&wordnet-ontology;Synset</xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
                ignore
            </a>
            <xsl:apply-templates select="lemon:LexicalEntry"/>
            <xsl:apply-templates select="wordnet-ontology:Synset"/>
            <small class="license_link"><a href="/license.html">License Information</a></small>
        </span>
    </xsl:template>

    <xsl:template name="properties">
        <xsl:for-each select="*">
            <xsl:sort select="concat(local-name(),@xml:lang)"/>
            <xsl:if test="namespace-uri()!='&lemon;' and namespace-uri()!='&rdfs;'">
                <tr class="rdf">
                    <!-- Hide lex_id -->
                    <xsl:if test="local-name()='lex_id'">
                        <xsl:attribute name="style">display:none;</xsl:attribute>
                    </xsl:if>
                    <td>
                        <a>
                            <xsl:attribute name="href">
                                <xsl:value-of select="concat(namespace-uri(),local-name())"/>
                            </xsl:attribute>
                            <xsl:choose>
                                <xsl:when test="local-name()='sameAs'">same as</xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="translate(local-name(),'_',' ')"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </a>
                    </td>
                    <td>
                        <xsl:choose>
                            <xsl:when test="local-name()='sense_tag'">
                                <xsl:variable name="position" select="substring-after(@rdf:resource,'#Component-')"/>
                                <xsl:call-template name="sense_tag">
                                    <xsl:with-param name="position" select="$position"/>
                                    <xsl:with-param name="index" select="1"/>
                                    <xsl:with-param name="text" select="substring-before(substring-after(@rdf:resource,'&wordnet;'),'#')"/>
                                    <xsl:with-param name="href" select="substring-after(@rdf:resource,'&wordnet;')"/>
                                </xsl:call-template>
                            </xsl:when>
                            <xsl:when test="@rdf:resource">
                                <a>
                                    <xsl:attribute name="href">
                                        <xsl:choose>
                                            <xsl:when
                                                    test="contains(@rdf:resource,'&wordnet;')">
                                                <xsl:value-of
                                                        select="substring-after(@rdf:resource,'&wordnet;')"/>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:value-of select="@rdf:resource"/>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:attribute>
                                    <xsl:attribute name="property">
                                        <xsl:value-of select="concat(namespace-uri(),local-name())"/>
                                    </xsl:attribute>
                                    <!-- Special mouse over for synsets-->
                                    <!--<xsl:if test="contains(@rdf:resource,'&wordnet-synset;')">
                                        <xsl:attribute name="id">
                                            <xsl:value-of select="concat(local-name(),substring-after(@rdf:resource,'&wordnet;'))"/>
                                        </xsl:attribute>
                                        <script>
                                           jQuery.get('title/<xsl:value-of select="substring-after(@rdf:resource,'&wordnet;')"/>', function(desc) { $('#<xsl:value-of select="concat(local-name(),substring-after(@rdf:resource,'&wordnet;'))"/>').attr('title',desc); }) 
                                       </script>
                                    </xsl:if>-->
                                   <xsl:choose>
                                        <xsl:when
                                                test="contains(@rdf:resource,'&wordnet-ontology;')">
                                            <xsl:value-of
                                                    select="translate(substring-after(@rdf:resource,'#'),'_',' ')"/>
                                        </xsl:when>
                                        <xsl:when test="contains(@rdf:resource,'&wordnet;')">
                                            <xsl:value-of
                                                    select="substring-after(@rdf:resource,'&wordnet;')"/>
                                        </xsl:when>
                                        <xsl:when test="contains(@rdf:resource,'&verbnet;')">
                                            <xsl:value-of
                                                select="concat('verbnet:',substring-after(@rdf:resource,'&verbnet;'))"/>
                                        </xsl:when>
                                        <xsl:when test="contains(@rdf:resource,'&lemonUby;')">
                                            <xsl:value-of
                                                select="concat('lemonUby:',substring-after(@rdf:resource,'&lemonUby;'))"/>
                                        </xsl:when>
                                        <xsl:when test="contains(@rdf:resource,'&w3c-wn;')">
                                            <xsl:value-of
                                                select="concat('w3c:',substring-after(@rdf:resource,'&w3c-wn;'))"/>
                                        </xsl:when>
                                        <xsl:when test="contains(@rdf:resource,'&lexvo-wn;')">
                                            <xsl:value-of
                                                select="concat('lexvo:',substring-after(@rdf:resource,'&lexvo-wn;'))"/>
                                        </xsl:when>
                                           <xsl:otherwise>
                                            <xsl:value-of select="@rdf:resource"/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </a>
                            </xsl:when>
                            <xsl:when test="rdf:Description">
                                <!-- This only happens for synset links so is not quite general yet -->
                                <a>
                                    <xsl:attribute name="href">
                                        <xsl:value-of select="rdf:Description/@rdf:about"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="property">
                                        <xsl:value-fo select="concat(namespace-uri(), local-name())"/>
                                    </xsl:attribute>
                                    <xsl:choose>
                                        <xsl:when
                                            test="contains(rdf:Description/@rdf:about,'&wordnet-ontology;')">
                                            <xsl:value-of
                                                select="translate(substring-after(rdf:Description/@rdf:about,'#'),'_',' ')"/>
                                        </xsl:when>
                                        <xsl:when test="contains(rdf:Description/@rdf:about,'&wordnet;')">
                                            <xsl:value-of
                                                select="substring-after(rdf:Description/@rdf:about,'&wordnet;')"/>
                                        </xsl:when>
                                        <xsl:when test="contains(rdf:Description/@rdf:about,'&verbnet;')">
                                            <xsl:value-of
                                                select="concat('verbnet:',substring-after(rdf:Description/@rdf:about,'&verbnet;'))"/>
                                        </xsl:when>
                                        <xsl:when test="contains(rdf:Description/@rdf:about,'&lemonUby;')">
                                            <xsl:value-of
                                                select="concat('lemonUby:',substring-after(rdf:Description/@rdf:about,'&lemonUby;'))"/>
                                        </xsl:when>
                                        <xsl:when test="contains(rdf:Description/@rdf:about,'&w3c-wn;')">
                                            <xsl:value-of
                                                select="concat('w3c:',substring-after(rdf:Description/@rdf:about,'&w3c-wn;'))"/>
                                        </xsl:when>
                                        <xsl:when test="contains(rdf:Description/@rdf:about,'&lexvo-wn;')">
                                            <xsl:value-of
                                                select="concat('lexvo:',substring-after(rdf:Description/@rdf:about,'&lexvo-wn;'))"/>
                                        </xsl:when>
                                           <xsl:otherwise>
                                               <xsl:value-of select="rdf:Description/@rdf:about"/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </a>
                                <table class="inner_rdf">
                                    <xsl:for-each select="rdf:Description">
                                        <xsl:call-template name="properties"/>
                                    </xsl:for-each>
                                </table>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:attribute name="property">
                                    <xsl:value-of select="concat(namespace-uri(),local-name())"/>
                                </xsl:attribute>
                                <xsl:if test="@rdf:datatype">
                                    <xsl:attribute name="datatype">
                                        <xsl:value-of select="@rdf:datatype"/>
                                    </xsl:attribute>
                                </xsl:if>
                                <xsl:if test="@xml:lang">
                                    <xsl:call-template name="lang">
                                        <xsl:with-param name="code" select="@xml:lang"/>
                                    </xsl:call-template>
                               </xsl:if>
                                <xsl:value-of select="."/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </td>
                </tr>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="lemon:LexicalEntry">
        <h1>
            <xsl:value-of select="lemon:canonicalForm/lemon:Form/lemon:writtenRep"/>
            <img src="http://www.w3.org/RDF/icons/rdf_w3c_icon.48.gif" height="28px" onclick="document.getElementById('rdf_format_list').style.display='inline';" style="float:right;"/>
        </h1>
        <xsl:call-template name="rdf_links"/>

        <table class="rdf">
            <tr class="rdf">
                <td>
                    <a href="&lemon;canonicalForm">canonical form</a>
                </td>
                <td>
                    <span id="CanonicalForm" resource="#CanonicalForm" rel="&lemon;canonicalForm" typeof="&lemon;Form">
                        <table class="inner_rdf">
                            <tr class="rdf">
                                <!--<td>
                                    <a href="&lemon;writtenRep">written representation</a>
                                </td>-->
                                <td property="&lemon;writtenRep">
                                    <xsl:attribute name="xml:lang">
                                        <xsl:value-of
                                                select="lemon:canonicalForm/lemon:Form/lemon:writtenRep/@xml:lang"/>
                                    </xsl:attribute>
                                    <xsl:value-of select="lemon:canonicalForm/lemon:Form/lemon:writtenRep"/>
                                </td>
                                <xsl:for-each select="lemon:canonicalForm/lemon:Form">
                                    <xsl:call-template name="properties"/>
                                </xsl:for-each>
                            </tr>
                        </table>
                    </span>
                </td>
            </tr>
            <xsl:if test="lemon:decomposition">
                <tr class="rdf">
                    <td>
                        <a href="&lemon;decomposition">decomposition</a>
                    </td>
                    <td>
                        <div class="rdf_component_list">
                            <xsl:for-each select="lemon:decomposition/rdf:Description">
                                <xsl:variable name="rdfid" select="@rdf:about"/>
                                <div class="rdf_component">
                                    <xsl:attribute name="resource">
                                        <xsl:value-of select="concat('_:elem',position())"/>
                                    </xsl:attribute>
                                    <xsl:if test="position()=1">
                                        <xsl:attribute name="rel">&lemon;decomposition</xsl:attribute>
                                    </xsl:if> 
                                    <xsl:choose>
                                        <xsl:when test="position()=last()">
                                            <a resource="&rdf;nil" property="&rdf;rest" style="display:none;">nil</a>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <a property="&rdf;rest" style="display:none;">
                                                <xsl:attribute name="resource">
                                                    <xsl:value-of select="concat('_:elem',position()+1)"/>
                                                </xsl:attribute>next
                                            </a>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                    <xsl:apply-templates select="//rdf:RDF/lemon:Component[@rdf:about=$rdfid]"/>
                                </div> 
                            </xsl:for-each>
                        </div>
                    </td>
                </tr> 
            </xsl:if>
            <xsl:for-each select="lemon:otherForm/lemon:Form">
                <tr class="rdf">
                    <td>
                        <a href="&lemon;otherForm">other form</a>
                    </td>
                    <td>
                        <span rel="&lemon;otherForm" typeof="&lemon;Form">
                            <xsl:attribute name="id">
                                <xsl:value-of select="substring-after(@rdf:about,'#')"/>
                            </xsl:attribute>
                            <xsl:attribute name="resource">
                                <xsl:value-of select="concat('#',substring-after(@rdf:about,'#'))"/>
                            </xsl:attribute>
                            <table class="inner_rdf">
                                <tr>
                                    <!--<td>
                                        <a href="&lemon;writtenRep">Written Representation</a>
                                    </td>-->
                                    <td property="&lemon;writtenRep">
                                        <xsl:attribute name="xml:lang">
                                            <xsl:value-of select="lemon:writtenRep/@xml:lang"/>
                                        </xsl:attribute>
                                        <xsl:value-of select="lemon:writtenRep"/>
                                    </td>
                                </tr>
                                <xsl:call-template name="properties"/>
                            </table>
                        </span>
                    </td>
                </tr>
            </xsl:for-each>
            <xsl:call-template name="properties"/>
            <xsl:for-each select="lemon:sense">
                <xsl:sort select="concat(@rdf:resource,lemon:LexicalSense/@rdf:about)"/>
                <tr class="rdf">
                    <td>
                        <a href="&lemon;sense">sense</a>
                    </td>
                    <td>
                        <span rel="&lemon;sense" typeof="&lemon;LexicalSense">

                            <xsl:choose>
                                <xsl:when test="@rdf:resource">
                                    <xsl:attribute name="id">
                                        <xsl:value-of select="substring-after(@rdf:resource,'#')"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="resource">
                                        <xsl:value-of select="concat('#',substring-after(@rdf:resource,'#'))"/>
                                    </xsl:attribute>
                                    <xsl:variable name="id" select="@rdf:resource"/>
                                    <xsl:apply-templates
                                            select="//lemon:LexicalSense[@rdf:about=$id]"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:attribute name="id">
                                        <xsl:value-of select="substring-after(lemon:LexicalSense/@rdf:about,'#')"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="resource">
                                        <xsl:value-of select="concat('#',substring-after(lemon:LexicalSense/@rdf:about,'#'))"/>
                                    </xsl:attribute>
                                    <xsl:apply-templates select="lemon:LexicalSense"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </span>
                    </td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>

    <xsl:template match="lemon:LexicalSense">
        <table class="inner_rdf">
            <tr class="rdf">
                <td>
                    <a href="&lemon;reference">synset</a>
                </td>
                <td>
                    <a property="&lemon;reference">
                        <xsl:attribute name="href">
                            <xsl:value-of select="substring-after(lemon:reference/@rdf:resource,'&wordnet;')"/>
                        </xsl:attribute>
                        <xsl:value-of select="substring-after(lemon:reference/@rdf:resource,'&wordnet;')"/>
                    </a>
                </td>
                <xsl:call-template name="properties"/>
            </tr>
        </table>
    </xsl:template>

    <xsl:template match="wordnet-ontology:Synset">
        <h1>
            <xsl:for-each select="rdfs:label">
                <xsl:sort select="text()"/>
                <xsl:value-of select="."/>
                <xsl:if test="not(position()=last())">, </xsl:if>
            </xsl:for-each>
                &#160;&#160;&#160;
            <img src="http://www.w3.org/RDF/icons/rdf_w3c_icon.48.gif" height="28px" onclick="document.getElementById('rdf_format_list').style.display='inline';" style="float:right;"/>
        </h1>
        <xsl:call-template name="rdf_links"/>
        <table class="rdf">
            <xsl:call-template name="properties"/>
        </table>
    </xsl:template>

    <xsl:template name="rdf_links">
            <ul id="rdf_format_list">
                <li class="rdf_format">
                    <a>
                        <xsl:attribute name="href">
                            <xsl:value-of select="concat(substring-after(@rdf:about,'&wordnet;'),'.json')"/>
                        </xsl:attribute>
                        JSON-LD
                    </a>
                </li>
                <li class="rdf_format">
                    <a>
                        <xsl:attribute name="href">
                            <xsl:value-of select="concat(substring-after(@rdf:about,'&wordnet;'),'.nt')"/>
                        </xsl:attribute>
                        N-Triples
                    </a>
                </li>
                <li class="rdf_format">
                    <a>
                        <xsl:attribute name="href">
                            <xsl:value-of select="concat(substring-after(@rdf:about,'&wordnet;'),'.ttl')"/>
                        </xsl:attribute>
                        Turtle
                    </a>
                </li>
                <li class="rdf_format">
                    <a>
                        <xsl:attribute name="href">
                            <xsl:value-of select="concat(substring-after(@rdf:about,'&wordnet;'),'.rdf')"/>
                        </xsl:attribute>
                        RDF/XML
                    </a>
                </li>
            </ul>
    </xsl:template>

    <xsl:template match="lemon:Component">
        <span rel="&rdf;first">
            <xsl:attribute name="id">
                <xsl:value-of select="substring-after(@rdf:about,'#')"/>
            </xsl:attribute>
            <xsl:attribute name="resource">
                <xsl:value-of select="concat('#',substring-after(@rdf:about,'#'))"/>
            </xsl:attribute>
            <span property="&rdfs;label">
                <xsl:attribute name="xml:lang">
                    <xsl:value-of select="rdfs:label/@xml:lang"/>
                </xsl:attribute>
                <xsl:value-of select="rdfs:label"/>
            </span>
        </span>
    </xsl:template>

    <xsl:template name="sense_tag">
        <xsl:param name="position"/>
        <xsl:param name="index"/>
        <xsl:param name="text"/>
        <xsl:param name="href"/>
        <xsl:choose>
            <xsl:when test="not(contains($text,'+'))">
                <xsl:choose>
                    <xsl:when test="$position=$index">
                        <a>
                            <xsl:attribute name="href">
                                <xsl:value-of select="$href"/>
                            </xsl:attribute>
                            <xsl:value-of select="substring-before($text,'-p')"/>
                        </a>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="substring-before($text,'-p')"/>
                    </xsl:otherwise> 
                </xsl:choose>
            </xsl:when> 
            <xsl:otherwise>
                <xsl:choose>
                    <xsl:when test="$position=$index">
                        <a>
                            <xsl:attribute name="href">
                                <xsl:value-of select="$href"/>
                            </xsl:attribute>
                            <xsl:value-of select="concat(substring-before($text,'+'),' ')"/>
                        </a>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="concat(substring-before($text,'+'),' ')"/>
                    </xsl:otherwise> 
                </xsl:choose>
                <xsl:call-template name="sense_tag">
                    <xsl:with-param name="position" select="$position"/>
                    <xsl:with-param name="index" select="$index + 1"/>
                    <xsl:with-param name="text" select="substring-after($text,'+')"/>
                    <xsl:with-param name="href" select="$href"/>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template name="lang">
        <xsl:param name="code"/>
        <xsl:attribute name="xml:lang">
            <xsl:value-of select="@xml:lang"/>
        </xsl:attribute>
        <xsl:if test="not(@xml:lang='eng')">
            <a>
                <xsl:attribute name="href">
                    <xsl:value-of select="concat('&lexvo;',@xml:lang)"/>
                </xsl:attribute>
                <xsl:choose>
                    <xsl:when test="$code='ara'">
                        <img src="/flag/sa.gif" title="Arabic (ara)"/>
                    </xsl:when>
                    <xsl:when test="$code='sqi'">
                        <img src="/flag/al.gif" title="Albanian (sqi)"/>
                    </xsl:when>
                     <xsl:when test="$code='zho'">
                         <img src="/flag/cn.gif" title="Chinese (zho)"/>
                    </xsl:when>
                     <xsl:when test="$code='dan'">
                         <img src="/flag/dk.gif" title="Danish (dan)"/>
                    </xsl:when>
                     <xsl:when test="$code='fas'">
                         <img src="/flag/ir.gif" title="Persian (fas)"/>
                    </xsl:when>
                     <xsl:when test="$code='fin'">
                         <img src="/flag/fi.gif" title="Finnish (fin)"/>
                    </xsl:when>
                     <xsl:when test="$code='fra'">
                         <img src="/flag/fr.gif" title="French (fra)"/>
                    </xsl:when>
                     <xsl:when test="$code='heb'">
                         <img src="/flag/il.gif" title="Hebrew (heb)"/>
                    </xsl:when>
                     <xsl:when test="$code='ita'">
                         <img src="/flag/it.gif" title="Italian (ita)"/>
                    </xsl:when>
                     <xsl:when test="$code='jpn'">
                         <img src="/flag/jp.gif" title="Japanes (jpn)"/>
                    </xsl:when>
                     <xsl:when test="$code='cat'">
                         <img src="/flag/catalonia.gif" title="Catalan (cat)"/>
                    </xsl:when>
                     <xsl:when test="$code='eus'">
                         <img src="/flag/basque.gif" title="Basque (eus)"/>
                    </xsl:when>
                     <xsl:when test="$code='glg'">
                         <img src="/flag/galicia.gif" title="Galician (glg)"/>
                    </xsl:when>
                     <xsl:when test="$code='spa'">
                         <img src="/flag/es.gif" title="Spanish (spa)"/>
                    </xsl:when>
                     <xsl:when test="$code='ind'">
                         <img src="/flag/id.gif" title="Bahasa Indonesia (ind)"/>
                    </xsl:when>
                     <xsl:when test="$code='zsm'">
                         <img src="/flag/my.gif" title="Bahasa Malay (zsm)"/>
                    </xsl:when>
                      <xsl:when test="$code='nno'">
                          <img src="/flag/no.gif" title="Nynorsk (nno)"/> (Nynorsk)
                    </xsl:when>
                      <xsl:when test="$code='nob'">
                          <img src="/flag/no.gif" title="Norwegian Bokm&#229;l (nob)"/> (Bokm&#229;l)
                    </xsl:when>
                      <xsl:when test="$code='pol'">
                          <img src="/flag/pl.gif" title="Polish (pol)"/>
                    </xsl:when>
                      <xsl:when test="$code='por'">
                          <img src="/flag/pt.gif" title="Portuguese (por)"/>
                    </xsl:when>
                      <xsl:when test="$code='tha'">
                          <img src="/flag/th.gif" title="Thai (tha)"/>
                    </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="@xml:lang"/>
                    </xsl:otherwise>
                </xsl:choose>
            </a>
            &#160;&#160;
        </xsl:if>
    </xsl:template>

</xsl:stylesheet>
