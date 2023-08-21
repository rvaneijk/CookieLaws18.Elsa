# content of conftest.py
from __future__ import absolute_import, division, print_function
import pytest


collect_ignore = ["openwpm-vanilla"]


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")
    parser.addoption("--runsluggish", action="store_true", default=False, help="run slow & sluggish tests")



def pytest_collection_modifyitems(config, items):
    if config.getoption("--runsluggish"):
        return  # option given to run slow & sluggish tests, don't skip anything
    skip_sluggish = pytest.mark.skip(reason="need --runsluggish option to run")
    for item in items:
        if "sluggish" in item.keywords:
            item.add_marker(skip_sluggish)  # skip sluggish
    if config.getoption("--runslow"):
    	return  # option given to run slow tests, don't skip them
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)  # skip slow
