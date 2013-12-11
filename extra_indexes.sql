CREATE INDEX IF NOT EXISTS k_morphmaps_wordid ON morphmaps (wordid);
CREATE INDEX IF NOT EXISTS k_morphmaps_morphid ON morphmaps (morphid);
CREATE INDEX IF NOT EXISTS k_phrasetypes_synsetid on [phrasetypes] ( synsetid );
CREATE INDEX IF NOT EXISTS k_morphs_morphid on [morphs] (morphid);
CREATE INDEX IF NOT EXISTS [idx_sensetags_new_sensekey] on [sensetags] ( [new_sensekey] );
CREATE TABLE [synsettriples] ([synsetid] INTEGER NOT NULL REFERENCES [synsets] ([synsetid]), property VARCHAR(80) NOT NULL, object VARCHAR(80) NOT NULL);
CREATE INDEX k_synsettriples_synsetid ON [synsettriples] ( synsetid );
CREATE TABLE [entrytriples] ([lemma] VARCHAR(80), [fragment] VARCHAR(80), property VARCHAR(80) NOT NULL, object VARCHAR(80) NOT NULL);
CREATE INDEX k_entrytriples_lemma ON [entrytriples] ( lemma );
