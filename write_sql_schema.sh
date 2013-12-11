#!/bin/bash

sqlite3 wordnet_3.1+.db << END
.schema adjpositions
.schema adjpositiontypes
.schema casedwords
.schema lexdomains
.schema lexlinks
.schema linktypes
.schema morphmaps
.schema morphs
.schema phrasetypes
.schema postypes
.schema samples
.schema senses
.schema sensetags
.schema semlinks
.schema synsets
.schema taggedtexts
.schema words
.schema vframesentencemaps
.schema vframesentences
END
