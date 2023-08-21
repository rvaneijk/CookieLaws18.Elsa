# Cookie Laws project main crawler
from __future__ import absolute_import, division, print_function
import json
import pandas as pd
import sys
import re

try:
    # import OpenWPM modules; needs a symlink (see readome)
    # if import doesn't work, we might be in docker, thus try importing from /opt
    from .automation import TaskManager, CommandSequence
except ImportError:
    sys.path.insert(0, '/opt/OpenWPM')
    from automation import TaskManager, CommandSequence


def read_crawl_list(filename, limit_tlds, rank_start, rank_end):
    # note: changed signature (20180519) tests might need update
    # read csv as dataframe
    f = filename if type(filename) is file else open(filename)
    df = pd.read_csv(f)
    assert "tld" in df.columns and "rank" in df.columns and "domain" in df.columns
    # select tlds
    df = df[df["tld"].isin(limit_tlds)] if limit_tlds else df  # .reset_index()?
    # copy selected sites
    sites = []
    for r in df.iterrows():
        tld, site, rank = r[1]["tld"], r[1]["domain"], r[1]["rank"]
        tld_multiplier = 2 if len(tld) != 2 else 1  # for gtlds use twice range
        if rank < rank_start * tld_multiplier or rank > rank_end * tld_multiplier:
            continue
        assert not site.startswith('http:') and not site.startswith('https:') \
            and site not in sites  # or just ignore if so..
        sites.append(site)
    return sites


def openwpm_instantiate(output_dir, num_browsers=1, banner_list=None, locale=None,
                        DBG_show_browser=False):
    # Set the manager preferences
    manager_params, browser_params = TaskManager.load_default_params(num_browsers)
    # Q: do we need to set: failure_limit?
    # TODO: set logger to INFO and make sure it works
    manager_params['failure_limit'] = 100
    manager_params['data_directory'] = output_dir
    manager_params['log_directory'] = output_dir

    # Configure browser preferences:
    # Instrumentat settings:
    # - we set http/js/cookie instruments (these record all http requests, cookies set, and
    #   js calls, but don't record the full html or js)
    # - we do not enable any tracking related firefox addon
    # - see OpenWPM README & test_openwpm.py for more info

    # Instrumentation notes:
    # - we don't change the User-Agent's as that might trigger anti-click-fraud (Rob)
    # - since 2016-12 openwpm uses an extension not mitm (thus proxy=F, extension=T)
    # - (btw, disable_webdriver_id=True, meaning?)

    for i in range(num_browsers):
        browser_params[i]['http_instrument'] = True  # save HTTP request and response headers
        browser_params[i]['js_instrument'] = True  # js call-logging for fingerprinting APIs
        browser_params[i]['cookie_instrument'] = True  # log changes to cookies (both js & http)
        browser_params[i]['headless'] = not DBG_show_browser
        browser_params[i]['banner_list_location'] = banner_list
        assert not browser_params[i]['donottrack']  # no DnT (could later change) -- default
        assert browser_params[i]['disable_flash']  # no Flash -- default
        # param to randomize user-agent might be interesting for future

        if locale:
            assert type(locale) is str or type(locale) is unicode
            assert 2 <= len(locale) <= 5  # e.g. 'fa' or 'de-at'
            locale = locale.lower() + ",en"  # or en-us?
            assert not browser_params[i]['prefs']
            # intl.accept_languages works (tested with DUCK.COM). intl.locale.x for is FF-UX
            browser_params[i]['prefs'] = {'intl.accept_languages': locale}

    # Instantiate & return the OpenWPM measurement platform objects
    # (we recreate this object, as there was a bug affecting logging on reuse of object,
    #  specifically i think with regards to changing the output folder)
    manager = TaskManager.TaskManager(manager_params, browser_params)
    return manager


def openwpm_crawl_sequence(site, timeout=90, detect_cookie_banner=True,
                           save_screenshot=True, dump_page_source=True,
                           browse_randomly=False):
    if not site.lower().startswith('http:') and not site.lower().startswith('https:'):
        site = 'http://' + site
    cs = CommandSequence.CommandSequence(site, reset=True)  # reset for stateless visit

    if not browse_randomly:
        cs.get(sleep=0, timeout=timeout)
    else:
        cs.browse(num_links=2, sleep=0, timeout=timeout)
        # TODO: test this -- API say can be used to visit random links in a page

    if detect_cookie_banner:
        cs.detect_cookie_banner(timeout=timeout)
    fnam = re.sub("[:/.]", "_", site.replace("http://", "").replace("https://", ""))
    if save_screenshot:
        # screenshot of only visible area (cropping not needed)
        cs.save_screenshot(fnam, timeout=timeout)
    if dump_page_source:
        # page source of top level frame (not everything, for performance. see test_openwpm.py)
        cs.dump_page_source(fnam, timeout=timeout)
    # note:
    # - cs.dump_profile_cookies() is not used anymore, see test_openwpm.py
    return cs
