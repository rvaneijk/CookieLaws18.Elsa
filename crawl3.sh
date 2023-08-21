#mkdir ./tmp
nohup docker run --privileged -v $PWD:/home/user openwpm python /home/user/crawl_script2.py --output-dir ./out/ --vpn-cc $1 --crawl-list ./indata/scanlist_20180423-fixping.csv --rank-start 1 --rank-end 100 --banner-list ./indata/bannerlist_201709.txt --vpn-hma-user ./indata/hma.cred --limit-tlds UK,NL,DE,JP,HU,SE,BE,FR,ES,CH,RO,COM,ORG,PT,AU,AT,US,CZ,IT,CA,GR,PL >> nolog.$1 &
# --browse-randomly
