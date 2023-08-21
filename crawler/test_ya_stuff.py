from __future__ import absolute_import, division, print_function
import pytest
import sys
from tempfile import TemporaryFile
import requests
from random import randint
from . import ya_logger, ya_httpd


def test_ya_logger():
    f = TemporaryFile()
    yal = ya_logger.Logger(logfile=f, console=True)
    yal.log("hello")
    f.seek(0)
    assert f.readlines() == ["hello\n"]


def test_ya_httpd():
    port = randint(10001, 30000)  # choose some random part
    httpd = ya_httpd.MyHTTPD(port)
    r = requests.get("http://127.0.0.1:%d" % port)
    assert r.status_code == 200
    hdr = httpd.get_seen_header()
    assert "accept-encoding" in hdr
