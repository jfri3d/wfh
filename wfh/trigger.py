import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from wfh.display.constants import INTERVAL, START_TIME, END_TIME
from wfh.display.inky_utils import update_inky

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

scheduler = BlockingScheduler()

if __name__ == "__main__":
    scheduler.add_job(update_inky)
    scheduler.add_job(update_inky,
                      CronTrigger(minute=f'0/{INTERVAL}',
                                  hour=f'{START_TIME}-{END_TIME}',
                                  day='*',
                                  month='*',
                                  day_of_week='0-4'))
    scheduler.start()
