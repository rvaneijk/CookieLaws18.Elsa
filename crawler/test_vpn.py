# Tests for crawler.vpn
from __future__ import absolute_import, division, print_function
import pytest
from os import path
from time import sleep
from tempfile import TemporaryFile
import pygeoip  # pip
from .vpn import VPNutil, VPN_HMA


def test_vpn_utils_basic():
    assert not VPNutil.is_route0_via_tun()
    ip0 = VPNutil.get_public_ip()  # could somehow validate this


def test_vpn_utils_ping():
    out = VPNutil.ping("127.0.0.1")
    assert out.startswith("PING 127.0.0.1 => 127.0.0.1 (127.0.0.1)")
    assert "=> 0.0" in out
    out = VPNutil.ping("somethingridicolous.outsideofthisworld")
    assert out.startswith("PING ERROR")


@pytest.mark.slow
def test_vpn_utils_ns():
    # Q: should we start by deleting the file, etc, if already set to 8.8.8.8?
    VPNutil.override_nameserver()
    OVERRIDEN_NS = "nameserver 8.8.8.8\n"
    assert open("/etc/resolv.conf").readlines()[0] == OVERRIDEN_NS
    VPNutil.reset_nameserver()
    assert open("/etc/resolv.conf").readlines()[0] != OVERRIDEN_NS


@pytest.mark.slow
def test_vpn_hma():
    # make sure no vpn before starting; get current ip
    assert not VPNutil.is_route0_via_tun()
    ip0 = VPNutil.get_public_ip()
    # geodb = pygeoip.GeoIP("./indata/GeoIP-106_20160705.dat", pygeoip.MEMORY_CACHE)  # 1.4s
    # cc0 = geodb.country_code_by_addr(ip0)

    # connect test
    hma = VPN_HMA(path.realpath("./indata/hma.cred"))  # Q: where should this file be?
    hma.connect("SE", disconnect_first=False, timeout=10)
    assert VPNutil.is_route0_via_tun()
    ip1 = VPNutil.get_public_ip()
    assert ip1 != ip0

    # disconnect test
    hma.disconnect()
    assert VPNutil.get_public_ip() == ip0
