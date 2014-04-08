<?xml version="1.0"?>
<!DOCTYPE xsl:stylesheet [
        <!ENTITY lemon   "http://lemon-model.net/lemon#">
        <!ENTITY wordnet-ontology   "http://wordnet-rdf.princeton.edu/ontology#">
        <!ENTITY wordnet "http://wordnet-rdf.princeton.edu/">
        <!ENTITY rdf   "http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <!ENTITY rdfs   "http://www.w3.org/2000/01/rdf-schema#">
        <!ENTITY verbnet "http://verbs.colorado.edu/verb-index/vn/">
        <!ENTITY lexvo "http://www.lexvo.org/page/iso639-3/">
        <!ENTITY owl "http://www.w3.org/2002/07/owl#">
        <!ENTITY lemonUby "http://lemon-model.net/lexica/uby/wn/">
        <!ENTITY w3c-wn "http://www.w3.org/2006/03/wn/wn20/instances/">
        ]>
 <xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:sparql="http://www.w3.org/2005/sparql-results#"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" >

    <xsl:template match="/sparql:sparql">
        <table class="sparql">
            <xsl:apply-templates select="sparql:head"/>
            <tbody>
                <xsl:apply-templates select="sparql:results"/>
            </tbody>
        </table>
    </xsl:template>

    <xsl:template match="sparql:head">
        <thead>
            <tr class="sparql_head">
                <xsl:for-each select="sparql:variable">
                    <th class="sparql_head"><xsl:value-of select="@name"/></th>
                </xsl:for-each>
            </tr>
        </thead>
    </xsl:template>

    <xsl:template match="sparql:results">
        <xsl:apply-templates select="sparql:result"/>
    </xsl:template>

    <xsl:template match="sparql:result">
        <xsl:variable name="row" select="."/>
        <tr class="sparql_body">
            <xsl:for-each select="//sparql:sparql/sparql:head/sparql:variable">
                <td class="sparql_body">
                    <xsl:variable name="var" select="@name"/>
                    <xsl:choose>
                        <xsl:when test="$row/sparql:binding[@name=$var]">
                            <xsl:apply-templates select="$row/sparql:binding[@name=$var]"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <i>Unbound</i>
                        </xsl:otherwise>
                    </xsl:choose>
                </td>
            </xsl:for-each>
        </tr>
    </xsl:template>

    <xsl:template match="sparql:binding">
        <xsl:apply-templates select="sparql:uri"/>
        <xsl:apply-templates select="sparql:literal"/>
        <xsl:apply-templates select="sparql:bnode"/>
    </xsl:template>

    <xsl:template match="sparql:uri">
        <a class="sparql_uri">
            <xsl:attribute name="href">
                <xsl:value-of select="."/>
            </xsl:attribute>
            <xsl:choose>
                <xsl:when test="contains(.,'&lemon;')">
                    <xsl:value-of select="concat('lemon:',substring-after(.,'&lemon;'))"/>
                </xsl:when>
                <xsl:when test="contains(.,'&wordnet-ontology;')">
                    <xsl:value-of select="substring-after(.,'&wordnet-ontology;')"/>
                </xsl:when>
                 <xsl:when test="contains(.,'&wordnet;')">
                    <xsl:value-of select="substring-after(.,'&wordnet;')"/>
                </xsl:when>
                 <xsl:when test="contains(.,'&rdf;')">
                    <xsl:value-of select="concat('rdf:',substring-after(.,'&rdf;'))"/>
                </xsl:when>
                 <xsl:when test="contains(.,'&rdfs;')">
                    <xsl:value-of select="concat('rdfs:',substring-after(.,'&rdfs;'))"/>
                </xsl:when>
                 <xsl:when test="contains(.,'&verbnet;')">
                    <xsl:value-of select="concat('verbnet:',substring-after(.,'&verbnet;'))"/>
                </xsl:when>
                 <xsl:when test="contains(.,'&lexvo;')">
                    <xsl:value-of select="concat('lexvo:',substring-after(.,'&lexvo;'))"/>
                </xsl:when>
                 <xsl:when test="contains(.,'&owl;')">
                    <xsl:value-of select="concat('owl:',substring-after(.,'&owl;'))"/>
                </xsl:when>
                 <xsl:when test="contains(.,'&lemonUby;')">
                    <xsl:value-of select="concat('lemonUby:',substring-after(.,'&lemonUby;'))"/>
                </xsl:when>
                 <xsl:when test="contains(.,'&w3c-wn;')">
                    <xsl:value-of select="concat('w3c-wn:',substring-after(.,'&w3c-wn;'))"/>
                </xsl:when>
                 <xsl:otherwise>
                    <xsl:value-of select="."/>
                </xsl:otherwise>
            </xsl:choose>
        </a>
    </xsl:template>

    <xsl:template match="sparql:literal">
        <span class="sparql_literal">
            <xsl:if test="@xml:lang">
                <xsl:attribute name="xml:lang">
                    <xsl:value-of select="@xml:lang"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:value-of select="."/>
        </span>
    </xsl:template>

    <xsl:template match="sparql:bnode">
        <span class="sparql_bnode">
            <xsl:value-of select="."/>
        </span>
    </xsl:template>      
</xsl:stylesheet>

