/* First ensure the following files are unzipped:
      wn30-31.csv
      wn20-30.csv
      w3c-wn20.csv
   Then execute this script as follows:
      sqlite3 mapping.db < mapping.sql
*/
CREATE TABLE wn30 ( wn31 int, wn30 varchar(80));
CREATE INDEX mapping_wn30 on wn30 (wn30);
CREATE TABLE wn20 ( wn20 varchar(10), wn30 varchar(10) );
CREATE INDEX mapping_wn20_20 on wn20 (wn20);
CREATE INDEX mapping_wn20_30 on wn20 (wn30);
CREATE TABLE w3c ( w3c varchar(80), wn20 varchar(10) );
CREATE INDEX w3c_wn20 on w3c (wn20);
CREATE INDEX w3c_w3c on w3c (w3c);
CREATE TABLE wn31r ( internal int, release int );
CREATE INDEX wn31r_r on wn31r (release) ;
CREATE INDEX wn31r_i on wn31r (internal) ;
.mode csv
.import wn30-31.csv wn30
.import wn20-30.csv wn20
.import w3c-wn20.csv w3c
.import wn31r2wn31i.csv wn31r

