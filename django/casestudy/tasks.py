from datetime import datetime
from celery import Celery
from celery.schedules import crontab
from pytz import timezone

from casestudy.models import Security
from django.casestudy import securities_client

app = Celery()
market_open = datetime.timetz(14, 30, 0, 0, pytz.UTC)
market_close = datetime.timetz(21, 0, 0, 0, pytz.UTC)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, update_security_prices)

    sender.add_periodic_task(
        crontab(second='*/5',
                hour='2,3,4,5,6,7,8',
                day_of_week='mon-fri')
    )

@periodic_task(run_every=timedelta(seconds=30))
def update_security_prices():
    print('update security prices')

@app.task
def update_available_securities():
    #stuff
    print('update available securities')
    securities_json = securities_client.get_tickers()
    securities = []
    for key, value in securities_json:
        securities.append(Security(ticker=key, name=value, exchange_name='NYSE'))
    

@worker_ready.connect
def at_start(sender, **k):
    with sender.app.connection() as conn:
        sender.app.send_task('update available securities')
        sender.app.send_task('update prices')
        now = datetime.utcnow()
        today = datetime.today()
        if 0 <= today.weekday() <= 4 and market_open <= now <= market_close:
            #start polling