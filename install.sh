#!/bin/bash
cp -a chrono.py /usr/local/bin
cp -a chrono.sh /usr/local/bin
cat /etc/rc.local | grep "/usr/local/bin/chrono.sh" >/dev/null || echo -e "Edit /etc/rc.local and add that line before \"Exit 0\":\n\n/usr/bin/xinit /usr/local/bin/chrono.sh $* -- :1\n\nSee rc.local.example"

