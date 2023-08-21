# Script to crawl for the Cookie-Law project
# Author: Hadi
# version 2.2 201805 (V2.1: 2018. V2: 24-Dec-2017; V1: 2016)
# This is the inner script that will be run from within Docker.
# I have made some changes to make it run smoother with Docker:
# - keep to one VPN/vantage (chosen from outer script)
# - ability to set start/end rank range within TLD
# - number of cpus = 1 (more than that sth messes up on networking)
# - automatically set working directory to script location (useful for docker paths)
# there is also new feature for setting locales + randomly browse scripts
#
# the outer script needs to pass in the necessary settings, run docker, capture the output
# (and obviously split the tasks among the inner processes)
from __future__ import absolute_import, division, print_function
from datetime import datetime
from os import getpid, path, getcwd, chdir, mkdir
# from multiprocessing import cpu_count
from argparse import ArgumentParser
from sys import argv
from time import time
import json
from crawler import engine  # has requirements re OpenWPM, see engine.py
from crawler import ya_logger
from crawler.vpn import VPN_HMA, VPNutil


# Parse command line options
parser = ArgumentParser(description="Script to crawl websites from ONE vantage point.")
parser.add_argument("--output-dir", required=True,
                    help="Output directory (stores sqlite, screenshots, HTML source)")
parser.add_argument("--crawl-list", required=True,
                    help="CSV file listing domains to crawl (needs header row marking"
                    " tld/rank/site columns).")
parser.add_argument("--banner-list", required=True,
                    help="File listing banner elements for detecting cookie banners/walls.")
parser.add_argument("--vpn-cc", required=True,
                    help="Country code of VPN/vantage point.")
parser.add_argument("--vpn-hma-user", required=True,
                    help="File with user/pass credentials for HMA VPN.")
parser.add_argument("--limit-tlds", required=True,
                    help="Only crawl domains with these TLDs (comma seperated).")
parser.add_argument("--rank-start", type=int, required=True,
                    help="Crawl domains starting from rank X within TLD.")
parser.add_argument("--rank-end", type=int, required=True,
                    help="Crawl domains ending with rank X within TLD.")

parser.add_argument("--browse-randomly", action="store_true",
                    help="Browse randomly for cookie-wall implicit consent.")
parser.add_argument("--skip-locale", action="store_true",
                    help="Skip changing the browser locale to match the vantage point.")
# other possible arguments: '--skip-cookiebanner', '--skip-screenshot', '--no-pagesource'

ARGS = parser.parse_args()
LIMIT_TLDS = [cc.upper().strip() for cc in ARGS.limit_tlds.split(',')]
NUM_BROWSERS = 1
OWPM_TIMEOUT = 90
chdir(path.dirname(path.realpath(__file__)))  # change wdir to script location -- for docker paths

OUTPUT_DIR = path.join(path.realpath(ARGS.output_dir),
                       "crawl-vpn%s-%s-%s" % (
                       ARGS.vpn_cc,
                       datetime.now().strftime("%Y%m%d.%H%M"),
                       getpid()))
mkdir(OUTPUT_DIR)
TIME0 = time()
logger = ya_logger.Logger(logfile=path.join(OUTPUT_DIR, 'crawl.log'), console=True)

locale_map = json.load(file("./crawler/locale_map.json"))
locale = locale_map[ARGS.vpn_cc.lower()] if not ARGS.skip_locale else None

sites = engine.read_crawl_list(ARGS.crawl_list,
                               LIMIT_TLDS,
                               ARGS.rank_start,
                               ARGS.rank_end)
# TODO: chekc no bad domains (second level tld) here
sites.insert(0, "geoip.hidemyass.com")  # check VPN geo IP

logger.log("Starting crawl (tlds:%d, rank:%d-%d => sites:%d) (output:%s)\n\n command: %s" % (
      len(LIMIT_TLDS), ARGS.rank_start, ARGS.rank_end, len(sites), OUTPUT_DIR, " ".join(argv)))

# Connect VPN. (could do a VPN speed test too)
vpn = VPN_HMA(user_cred_file=path.realpath(ARGS.vpn_hma_user))
vpn.connect(ARGS.vpn_cc)
logger.log("VPN connected to %s (type:%s locale:%s IP:%s NS:%s)" % (
        ARGS.vpn_cc, str(vpn), locale, VPNutil.get_public_ip(), VPNutil.get_nameserver()))

manager = engine.openwpm_instantiate(OUTPUT_DIR,
                                     NUM_BROWSERS,
                                     path.realpath(ARGS.banner_list),
                                     locale)
for i, site in enumerate(sites):
    # Commands to visit site, save screenshot & html source, detect cookie banners
    # Notes:
    # - Saving site ip/geo stuff, if needed, should be in separate debug-logs...
    # - Assert is to ensure we don't crawl w/o vpn by accident
    # - Cropping of images used to be needed here, not anymore
    # - testing implicit consent by browsing (random) links on page: randomly_browse=True
    cs = engine.openwpm_crawl_sequence(site, browse_randomly=ARGS.browse_randomly)
    # TODO: need to make sure the random browsing has no issues with screenshot
    assert VPNutil.is_route0_via_tun()
    manager.execute_command_sequence(cs)
    logger.log("Visit #%d: %s @%.fs" % (i + 1, site, time()-TIME0))
    logger.log(VPNutil.ping(site))


manager.close()
vpn.disconnect()

logger.log("Finished crawl (time: %.fs)" % (time() - TIME0))
