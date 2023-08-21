# Tests for crawler.engine
from __future__ import absolute_import, division, print_function
import pytest
import json
import os
from shutil import rmtree
import BaseHTTPServer as server  # on py3: http.server as ...
from SocketServer import TCPServer
from random import randint
from tempfile import TemporaryFile, mkdtemp
from sys import stderr
from time import sleep
from .automation import TaskManager, CommandSequence
from . import engine, ya_httpd


# def test_read_config():
#     # first, write the xxx.config as a temp json file
#     f = TemporaryFile()
#     d = {"NUM_BROWSERS": 3, "LIMIT_TLDS": ["BE", "FR", "DE", "NL", "COM", "ORG"]}
#     json.dump(d, f)
#     # now test loading temp file
#     f.seek(0)
#     cfg = engine.read_config(f)
#     assert type(cfg) is dict
#     assert type(cfg["LIMIT_TLDS"]) is list
#     # now test loading a real config file
#     cfg = engine.read_config("./indata/simple.config")
#     # (Q: where should test data reside? also, run tests from root)
#     assert type(cfg) is dict
#     # (could test for all mandatory elements?)


def test_read_crawl_list():
    tst = "tld,rank,rank_global,domain,cat\nAT,1,11756,google.at,enter\nAT,2,29536,gotomeet.at,\n"
    f = TemporaryFile()
    f.write(tst)
    f.seek(0)
    sites = engine.read_crawl_list(f)
    assert sites == ["google.at", "gotomeet.at"]


# @pytest.mark.slow
# def test_openwpm_instantiate():
#     # test notes: - can we have a faster version that doesn't run FF?
#     #             - can we check taskmanager browser settings?
#     # test requires: the symlinks to OpenWPM/automation & firefox-bin to exist
#     tmpdir = mkdtemp()
#     manager = engine.openwpm_instantiate(tmpdir)
#     assert isinstance(manager, TaskManager.TaskManager)
#     rmtree(tmpdir)  # remove temp with all contents!


def test_openwpm_crawl_sequence_creation():
    cs = engine.openwpm_crawl_sequence('somesite.com')
    assert isinstance(cs, CommandSequence.CommandSequence)


@pytest.mark.slow
def test_openwpm_set_locale():
    tmpdir = mkdtemp()
    port = randint(10001, 30000)  # choose some random part
    httpd = ya_httpd.MyHTTPD(port)  # run a local http server

    manager = engine.openwpm_instantiate(tmpdir, locale="fa")  # set locale
    cs = engine.openwpm_crawl_sequence('127.0.0.1:%d' % port,
                                       detect_cookie_banner=False,
                                       dump_page_source=False,
                                       save_screenshot=False)
    manager.execute_command_sequence(cs)

    hdr = httpd.get_seen_header(timeout=30)  # wait fo visit
    assert hdr["accept-language"].startswith("fa,en")  # check if locale was set
    rmtree(tmpdir)  # remove temp with all contents!


@pytest.mark.slow
def test_openwpm_test_browse_randomly():
    tmpdir = mkdtemp()
    port = randint(10001, 30000)  # choose some random part
    html = "<html>This is some page with two random links<a href='/link1'>this</a>" \
        "and <a href='/link2'>that</a></html>"
    httpd = ya_httpd.MyHTTPD(port, html_to_serve=html)  # run a local http server

    manager = engine.openwpm_instantiate(tmpdir)
    cs = engine.openwpm_crawl_sequence('127.0.0.1:%d' % port,
                                       detect_cookie_banner=False,
                                       dump_page_source=False,
                                       save_screenshot=False,
                                       browse_randomly=True)
    manager.execute_command_sequence(cs)

    # three visits (excludes favoicon)
    hdr = httpd.get_seen_header(timeout=10)
    assert hdr["PATH"] == "/"
    for i in range(2):
        hdr = httpd.get_seen_header(timeout=5)
        assert hdr["PATH"] in ("/link1", "/link2")

    sleep(2)
    rmtree(tmpdir)  # remove temp with all contents!
