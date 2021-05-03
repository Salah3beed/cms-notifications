#!/usr/bin/env python3
from crontab import CronTab
import getpass
# Hello sir, how's your day how shall i persume your help ? hello dear, how can i help you ?
import os
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
print(BASE_DIR)
my_cron = CronTab(user='salah3beed')
job = my_cron.new(command='python '+BASE_DIR+'/a.py')
job.minute.every(1)
my_cron.write()

