#!/bin/sh
/usr/sbin/sshd
echo "=================================" >> /home/app/log/app.log
date >> /home/app/log/app.log

# Installing the python dependencies
cd /home/app/src/Service
pip install gunicorn-19.9.0-py2.py3-none-any.whl >> /home/app/log/app.log 2>> /home/app/log/app.log
pip install futures-2.2.0-py2.py3-none-any.whl >> /home/app/log/app.log 2>> /home/app/log/app.log
pip install configparser-4.0.2-py2.py3-none-any.whl >> /home/app/log/app.log 2>> /home/app/log/app.log

# Starting the data fetch process
python /home/app/src/Service/data_fetch.py >> /home/app/log/app.log 2>> /home/app/log/app.log &

# Starting the web server
gunicorn -b "0.0.0.0:80" -t 300 -w 4 app:app >> /home/app/log/app.log 2>> /home/app/log/app.log


echo "=================================" >> /home/app/log/app.log
