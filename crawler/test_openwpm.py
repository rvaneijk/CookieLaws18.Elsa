# Tests of OpenWPM basic functionality
from __future__ import absolute_import, division, print_function
from .automation import TaskManager, CommandSequence


def test_instrumentation():
    # REFERNECES:
    # - OpenWPM README for information
    # - https://github.com/citp/OpenWPM/blob/master/automation/default_manager_params.json
    # - https://github.com/citp/OpenWPM/blob/master/automation/default_browser_params.json

    # instrumentation settings (based on OpenWPM's README):
    # - http_instrument: saves (HTTP request and response headers, redirects, and POST bodies)
    #                    to the http_requests, http_responses, and http_redirects tables.
    # - js_instrument: saves (all javascript calls) to the 'javascript' table.
    # - cookie_instrument: saves (cookies set by js & http) to 'javascript_cookies' table.
    #                      documentation states this is _experperimental_.
    # - cp_instrument: saves (content policy calls -- what caused a request) to 'content_policy'
    #                  table. also experimental.
    # - save_all_content: records ALL crawl files in a LevelDB; -- may cause performance issues
    # - save_javascript: like above, but saves only javascript files

    # command-sequence methods (based on OpenWPM README):
    # - .dump_profile_cookies(): saves FF cookies.sqlite contents to 'profile_cookies' table.
    #                            (according to Steve, this might be buggy)
    # - .dump_page_source(): saves top-level frames rendered html...  (HA: only somewhat useful)
    # - .dump_flash_cookies(): saves flash cookies to 'flash_cookies' table.
    # - .save_screenshot(): screenshot of the visible frame (there is a full version too)
    #

    # other settings (based on OpenWPM README):
    # - leaving as is: bot_mitigation=disabled (dont appear as a bot), flash=disabled (default)
    #                  donottrack=diabled, tp_cookies=always (FF 3rd-party cookie settings)
    # - not enabling addons: disonnect, ghostery, https-everywhere, ublock-origin
    # - state: important to reset! (do)

    # => THUS: set of http_instrument/js_instrument/cookie_instrument to True & not others OK.

    pass
