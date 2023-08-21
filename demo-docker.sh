docker run --privileged -v $PWD:/home/user openwpm python /home/user/crawl_script.py --output-dir ./tmp --vantages DE,ES --crawl-list ./indata/scanlist_20171223.csv --limit-tlds NL,DE,ES,COM --limit-per-tld 1 --banner-list ./indata/bannerlist_201709.txt --vpn-hma-user ./indata/hma.cred --set-workdir --num-browsers 2