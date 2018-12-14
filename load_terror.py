# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 19:53:00 2018

@author: nagy4
"""
import psycopg2
import csv
conn = psycopg2.connect("host=localhost dbname=pdt_project user=postgres password=pg")

cur = conn.cursor()
cur.execute("""
CREATE TABLE attacks(
    year integer,
    month integer,
    day integer,
    country integer,
    country_text text,
    region integer,
    region_text text,
    provstate text,
    city text,
    latitude numeric,
    longitude numeric,
    attack_type integer,
    attack_type_text text,
    target_type integer,
    target_type_text text,
    target_sub_type integer,
    target_sub_type_text text,
    gname text,
    weap_type integer,
    weap_type_text text,
    nkill integer
)
""")

with open('globalterrorismdb_0718dist.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row.
    for row in reader:
        cur.execute(
            "INSERT INTO attacks VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            row
        )
conn.commit()


cur.execute("alter table attacks add column geom geometry(Point, 4326)")
cur.execute("update attacks set geom=st_SetSrid(st_MakePoint(longitude, latitude), 4326)")
conn.commit()