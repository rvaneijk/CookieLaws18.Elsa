# run w/o priveleges, w/o VPN, one browser, no banner list, output /tmp
docker run -v $PWD:/home/user openwpm python /home/user/crawl_script-simple.py --output-dir /tmp --crawl-list ./indata/scanlist_20171223.csv --limit-tlds NL,DE,ES,COM --limit-per-tld 1 --set-workdir
