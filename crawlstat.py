#!/usr/bin/python
# Script to give quick stats about a crawl
# Author Hadi, 25 May 2018
from __future__ import print_function, division
import pandas as pd  # sudo dnf install python3-pandas
import numpy as np
from sys import argv
import sqlite3
from os import path
from glob import glob

for inpath in argv[1:]:
    print("*********", inpath)
    fnam = path.join(inpath, "crawl-data.sqlite")
    if not path.isfile(fnam):
        continue

    try:
        # open sqlite. readonly (e.g. ?mode=ro) might be safer re multiprocess
        # (but needs to be figured out -- for now do just the quick stuff)
	dbcon = None
        dbcon = sqlite3.connect(fnam)
        sites = pd.read_sql_query("""SELECT s.visit_id, site_url as site, bool_success,
                                  group_concat(response_status) as response_status,
                                  group_concat(location) as redirect, count(*) as response_count
                                  FROM site_visits s
                                  LEFT JOIN CrawlHistory h ON s.site_url=h.arguments
                                            AND h.command='GET'
                                  LEFT JOIN http_responses r ON s.visit_id=r.visit_id
                                            AND LOWER(RTRIM(s.site_url))=RTRIM(r.url, '/')
                                  GROUP BY s.visit_id""",
                                  dbcon)
        t = sites.groupby('bool_success').count().site
        print("\tvisits:", t[1], "+", t[0], "+", t[-1])
        # cookies = pd.read_sql_query("""SELECT site_url as site, host, name, value, is_session
        #                             FROM site_visits s
        #                             LEFT JOIN javascript_cookies c
        #                             ON s.visit_id=c.visit_id ORDER BY s.visit_id""",
        #                             dbcon)
        # print("\tavg. cookies:", np.mean(cookies.groupby("site").count().is_session))
    except Exception as x:
        print("\tsqlite ex: %s" % str(x))
    if dbcon:
        dbcon.close()

    print("\tscreenshots: ", len(glob(path.join(inpath, "screenshots", "*"))))
    # print("\tpage sources: ", len(glob(path.join(inpath, "sources/*"))))
