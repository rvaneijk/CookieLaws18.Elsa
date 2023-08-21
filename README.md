# CookieLaws18

- Setup: create a virtualenv (Python 2); install requirements via pip

    mkvirtualenv cookielaws  
    pip install -r requirements-openwpm-plus.txt


- create a symlink to openwpm/automation in crawler directory:
    (e.g. assuming OpenWPM cloned under ~/devel/ & install.sh has downloaded firefox)
    ln -s ~/devel/OpenWPM/automation/ crawler/
    ln -s ~/devel/OpenWPM/firefox-bin/ crawler/


- make sure openwpm docker is also built
    ("docker build -f docker/Dockerfile -t openwpm ." from within OpenWPM source directory)

- testing

    workon cookielaws
    pytest  # goes through all  examples



- (run scripts directly; via docker)
