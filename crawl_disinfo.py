# Script to crawl for the DisInformation Project (based on Cookie-Laws project)
# Author: Hadi
# Version: 2018-04-17
from __future__ import absolute_import, division, print_function
from datetime import datetime
from os import getpid, path, getcwd, chdir, mkdir
from multiprocessing import cpu_count
from argparse import ArgumentParser
from sys import argv
from time import time
from crawler import engine, ya_logger  # has requirements re OpenWPM, see engine.py

# chdir(path.dirname(path.realpath(__file__)))
CRAWL_LIST = "indata/disinfo-tracker-site-list-201804.csv"
BANNER_LIST = "indata/bannerlist_201709.txt"
NOW = datetime.now().strftime("%Y%m%d.%H%M")
OUTPUT_DIR = path.join(path.realpath("out"), "disinfo." + NOW)
NUM_BROWSERS = 1
OWPM_TIMEOUT = 60
TIME0 = time()

# Setup logger, load site list, setup VPN
mkdir(OUTPUT_DIR)
logger = ya_logger.Logger(logfile=path.join(OUTPUT_DIR, 'crawl.log'), console=True)
sites = engine.read_crawl_list(CRAWL_LIST)
sites.insert(0, "geoip.hidemyass.com")  # check location, FYI

logger.log("Starting crawl (PID:%d CPUs:%d/%d VPN:%s sites:%d time:%s CWD:%s)\n\n command: %s" % (
    getpid(), NUM_BROWSERS, cpu_count(), "--", len(sites), NOW, getcwd(), " ".join(argv)))

# Loop over vantages, then sites, and send crawl commands

manager = engine.openwpm_instantiate(OUTPUT_DIR,
                                     NUM_BROWSERS,
                                     BANNER_LIST,
                                     set_locale=False,
                                     DBG_show_browser=True)
for site in sites:
    # Commands to visit site, save screenshot & html source, detect cookie banners
    # Notes:
    # - Saving site ip/geo stuff, if needed, should be in separate debug-logs...
    # - Assert is to ensure we don't crawl w/o vpn by accident
    # - Cropping of images used to be needed here, not anymore
    # - LATER test implicit consent by browsing (random) link(s) on page (rob wants too)
    cs = engine.openwpm_crawl_sequence(site)
    # assert VPNutil.is_route0_via_tun()
    manager.execute_command_sequence(cs)

manager.close()


logger.log("Finished crawl (time: %.fs)" % (time() - TIME0))
