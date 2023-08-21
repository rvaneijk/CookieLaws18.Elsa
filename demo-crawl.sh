#mkdir ./tmp
python crawl_script.py --output-dir ./tmp/ --vantages ES --crawl-list ./indata/scanlist_20180421.csv --limit-per-tld 1 --banner-list ./indata/bannerlist_201709.txt --vpn-hma-user ./indata/hma.cred
