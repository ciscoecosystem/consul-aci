#!/bin/sh
/usr/sbin/sshd
echo "=================================" >> /home/app/log/app.log
date >> /home/app/log/app.log
# pip install graphene >> /home/app/log/app.log
# pip install flask_graphql >> /home/app/log/app.log
# pip install gunicorn >> /home/app/log/app.log
cd /home/app/src/Service
pip install gunicorn-19.9.0-py2.py3-none-any.whl
pip install futures-2.2.0-py2.py3-none-any.whl
pip install configparser-4.0.2-py2.py3-none-any.whl
gunicorn -b "0.0.0.0:80" -t 300 -w 2 app:app >> /home/app/log/app.log 2>> /home/app/log/app.log


echo "=================================" >> /home/app/log/app.log

# python /home/app/src/Service/app.py >> /home/app/log/app.log 2>> /home/app/log/app.log
# python /home/app/src/Service/main_thread.py >> /home/app/log/main_thread.log 2>> /home/app/log/main_thread.log
