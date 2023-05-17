#!/bin/bash

distributive=$(hostnamectl | grep -E 'Transient hostname: .+')

curl -sSL https://install.python-poetry.org | python3 -
poetry install

if [ "$distributive" == 'Transient hostname: ubuntu' ]; then
    sudo apt-get install supervisor
fi

sudo systemctl start supervisor
sudo systemctl enable supervisor

if [ -e /etc/supervisor/conf.d/shop_bot.conf ]; then
    cat << EOF | sudo tee /etc/supervisor/conf.d/shop_bot.conf >/dev/null
[program:shop_bot]
command=python3 app.py
directory=/root/shop_bot/src/
autostart=true
autorestart=true
startretries=10
stopsignal=KILL
startsecs=1
redirect_stderr=true
user=root
killasgroup=true
stopasgroup=true
EOF
fi

sudo supervisorctl start shop_bot

