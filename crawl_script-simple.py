# Script to crawl for the Cookie-Law project
# Author: Hadi
# version 2.1 (V2: 24-Dec-2017; V1: 2016)
from __future__ import absolute_import, division, print_function
from datetime import datetime
from os import getpid, path, getcwd, chdir, mkdir
from multiprocessing import cpu_count
from argparse import ArgumentParser
from sys import argv
from time import time
from crawler import engine, ya_logger  # has requirements re OpenWPM, see engine.py
from crawler.vpn import VPN_HMA, VPNutil


# Parse command line options
parser = ArgumentParser(description="Script to crawl websites from multiple vantage points.")
parser.add_argument("--output-dir", required=True,
                    help="Output directory (stores sqlite, screenshots, HTML source)")
#parser.add_argument("--vantages", required=True,
#                    help="Country codes of vantage points (comma separated).")
parser.add_argument("--crawl-list", required=True,
                    help="CSV file listing domains to crawl (needs header row marking"
                    " tld/rank/site columns).")
#parser.add_argument("--banner-list", required=True,
#                    help="File listing banner elements for detecting cookie banners/walls.")
#parser.add_argument("--vpn-hma-user", required=True,
#                    help="File with user/pass credentials for HMA VPN.")
parser.add_argument("--limit-tlds",
                    help="Only crawl domains with these TLDs (comma seperated).")
parser.add_argument("--limit-per-tld", type=int,
                    help="Only crawl these many domains per TLD (ordered by rank).")
parser.add_argument("--num-browsers", type=int,
                    help="Number of Firefox browsers to run in parallel.")
parser.add_argument("--set-workdir", action="store_true",
                    help="Change the working directory to script location (useful for Docker).")
parser.add_argument("--set-locale", action="store_true",
                    help="Change the browser locale to match the vantage point.")
# other possible arguments: '--skip-cookiebanner', '--skip-screenshot', '--no-pagesource'
ARGS = parser.parse_args()

# convert arguments, set some defaults
if ARGS.set_workdir:
    chdir(path.dirname(path.realpath(__file__)))
NOW = datetime.now().strftime("%Y%m%d.%H%M")
OUTPUT_DIR = path.join(path.realpath(ARGS.output_dir), "crawl." + NOW)
#VANTAGES = [cc.upper().strip() for cc in ARGS.vantages.split(',')]  # user should avoid duplicates
LIMIT_TLDS = [cc.upper().strip() for cc in ARGS.limit_tlds.split(',')] if ARGS.limit_tlds else []
NUM_BROWSERS = ARGS.num_browsers or 1
OWPM_TIMEOUT = 60
CHECK_VPN_GEOIP = "geoip.hidemyass.com"
TIME0 = time()

# Setup logger, load site list, setup VPN
mkdir(OUTPUT_DIR)
logger = ya_logger.Logger(logfile=path.join(OUTPUT_DIR, 'crawl.log'), console=True)
sites = engine.read_crawl_list(ARGS.crawl_list, LIMIT_TLDS, ARGS.limit_per_tld)
sites.insert(0, CHECK_VPN_GEOIP)
vpn = "novpn"  # VPN_HMA(user_cred_file=path.realpath(ARGS.vpn_hma_user))

logger.log("Starting crawl (PID:%d CPUs:%d/%d VPN:%s sites:%d time:%s CWD:%s)\n\n command: %s" % (
    getpid(), NUM_BROWSERS, cpu_count(), str(vpn), len(sites), NOW, getcwd(), " ".join(argv)))

# Loop over vantages, then sites, and send crawl commands
for vcc in ["novpn"]:  #VANTAGES:
    #vpn.connect(vcc)

    logger.log("VPN connected to %s (IP:%s time:%.fs NS:%s)" % (
        vcc, VPNutil.get_public_ip(), time() - TIME0, VPNutil.get_nameserver()))
    # (Note: could do VPN speed test too)

    manager = engine.openwpm_instantiate(path.join(OUTPUT_DIR, "from-" + vcc),
                                         NUM_BROWSERS) #,
                                         #path.realpath(ARGS.banner_list),
                                         #ARGS.set_locale)
    for site in sites:
        # Commands to visit site, save screenshot & html source, detect cookie banners
        # Notes:
        # - Saving site ip/geo stuff, if needed, should be in separate debug-logs...
        # - Assert is to ensure we don't crawl w/o vpn by accident
        # - Cropping of images used to be needed here, not anymore
        # - LATER test implicit consent by browsing (random) link(s) on page (rob wants too)
        cs = engine.openwpm_crawl_sequence(site)
        #assert VPNutil.is_route0_via_tun()
        manager.execute_command_sequence(cs)

	break #hadi

    manager.close()
    #vpn.disconnect()

logger.log("Finished crawl (time: %.fs)" % (time() - TIME0))
