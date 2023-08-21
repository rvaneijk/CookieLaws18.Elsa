OWPM_DIR=~/Devel/OpenWPM/
cp Dockerfile2 $OWPM_DIR/docker/
cp requirements-openwpm-plus.txt $OWPM_DIR/requirements-openwpm-plus2.txt
cd $OWPM_DIR
docker build -f docker/Dockerfile2 -t openwpm .
