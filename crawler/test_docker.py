# Tests for running OpenWPM & our crawler from within Docker
from __future__ import absolute_import, division, print_function
from subprocess import call, check_output
from tempfile import mkdtemp
from os import path, listdir
from glob import glob
import shutil
import pytest
import sqlite3


def test_script_exists():
    # return  # TMP
    r = call(["python", "crawl_script.py"])
    assert r == 2  # should give error without parameters


@pytest.mark.sluggish
def test_script():
    # veyr slow :) -- takes about 3 minutes
    tmpdir = mkdtemp()
    vantages, lim_ctlds, lim_gtlds, lim_per = ["DE", "ES"], ["NL", "DE", "ES"], ["COM"], 1
    cmd = ["python", "crawl_script.py",
           "--output-dir", tmpdir,
           "--vantages", ",".join(vantages),
           "--crawl-list", "./indata/scanlist_20171223.csv",
           "--limit-tlds", ",".join(lim_ctlds + lim_gtlds),
           "--limit-per-tld", str(lim_per),
           "--banner-list", "./indata/bannerlist_201709.txt",
           "--vpn-hma-user", "./indata/hma.cred",
           "--num-browsers", "2"]
    print(cmd)
    r = call(cmd)
    assert r == 0

    # check main subdirectories: crawl.20180305.1509/from-[DE|ES]
    ld = listdir(tmpdir)
    assert len(ld) == 1 and 'crawl' in ld[0]
    tmpdir = path.join(tmpdir, ld[0])
    assert len(listdir(tmpdir)) == len(vantages) + 1  # +1=crawl.log

    # TODO: check VPN messages / IPs in logs

    # check for screenshot & sources under each subdir (allow for 2 timeout errors)
    expected_crawls = len(lim_ctlds)*lim_per + len(lim_gtlds)*lim_per*2 + 1  # +1=geo
    for vcc in vantages:
        assert len(glob(tmpdir + '/*%s/screenshots/*png' % vcc)) >= expected_crawls - 2
        assert len(glob(tmpdir + '/*%s/sources/*html' % vcc)) >= expected_crawls - 2

    # check sqlite contains what's expected
    for vcc in vantages:
        sqlf = glob(tmpdir + "/*%s/crawl-data.sqlite" % vcc)
        assert len(sqlf) == 1
        with sqlite3.connect(sqlf[0]) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM site_visits")
            assert cur.fetchone() == (6,)
            cur.execute("SELECT COUNT(*) FROM javascript_cookies")
            assert cur.fetchone() > (10,)
            cur.execute("SELECT COUNT(*) FROM cookie_banners")
            assert cur.fetchone() > (1,)

    shutil.rmtree(tmpdir)


def test_docker_basics():
    # checks if docker installed & openwpm container has been built
    # (build instructions: OpenWPM.git/docker/README.md)
    r = call(["docker", "run", "openwpm"])  # raises if: docker not installed
    assert r == 0  # asserts if: openwpm container doesn't exist

    # next, create a temp script; pass it to docker; confirm output;
    tmpdir = mkdtemp()
    with open(path.join(tmpdir, "mytmp.py"), "w") as f:
        f.write("from __future__ import print_function\nprint('HELLO LOVELY WORLD')")
    # Q: do we need '-it' switch?
    out = check_output(["docker", "run",
                        "-v", "%s:/home/user" % tmpdir,
                        "openwpm",
                        "python", "/home/user/mytmp.py"])
    assert out == "HELLO LOVELY WORLD\n"
    shutil.rmtree(tmpdir)

    # finally, check mapping to run crawl script
    curdir = path.dirname(path.dirname(path.realpath(__file__)))  # map project root
    cmd = ["docker", "run",
           "--privileged",  # required for openvpn
           "-v", "%s:/home/user" % curdir,
           "openwpm",
           "python", "/home/user/crawl_script.py"]
    r = call(cmd)
    assert r == 2


@pytest.mark.sluggish
def test_script_via_docker():
    # very slow!
    curdir = path.dirname(path.dirname(path.realpath(__file__)))  # map project root
    tmpdir = mkdtemp(dir=path.join(curdir, 'tmp'))
    vantages, lim_ctlds, lim_gtlds, lim_per = ["DE", "ES"], ["NL", "DE", "ES"], ["COM"], 1
    cmd = ["docker", "run",
           "--privileged",  # required for openvpn; docker's user can sudo wo pass
           "-v", "%s:/home/user" % curdir,  # cool mapping for in/out
           "openwpm",
           "python", "/home/user/crawl_script.py",  # great that crawler finds 'automation'
           "--output-dir", tmpdir.replace(curdir, "."),
           "--vantages", ",".join(vantages),
           "--crawl-list", "./indata/scanlist_20171223.csv",
           "--limit-tlds", ",".join(lim_ctlds + lim_gtlds),
           "--limit-per-tld", str(lim_per),
           "--banner-list", "./indata/bannerlist_201709.txt",
           "--vpn-hma-user", "./indata/hma.cred",
           "--set-workdir",
           "--num-browsers", "2"]
    print(" ".join(cmd))
    r = call(cmd)
    ld = listdir(tmpdir)
    assert len(ld) == 1 and 'crawl' in ld[0]
    tmpdir = path.join(tmpdir, ld[0])
    assert len(listdir(tmpdir)) == len(vantages) + 1  # +1=crawl.log
    assert r == 0
    # could add more checks, but this should be sufficent
    # shutil.rmtree(tmpdir)  #leave for inspection
