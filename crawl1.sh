#mkdir ./tmp
docker run --privileged -v $PWD:/home/user openwpm python /home/user/crawl_script.py --set-workdir --num-browsers 2 --output-dir ./out/ --vantages GB,NL,DE,US --crawl-list ./indata/scanlist_20171223.csv --limit-tlds UK,NL,DE,US,COM --limit-per-tld 30 --banner-list ./indata/bannerlist_201709.txt --vpn-hma-user ./indata/hma.cred 
