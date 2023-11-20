from datetime import datetime, timezone
from celery import Celery, shared_task
from celery.signals import worker_ready
from celery.schedules import crontab
import pytz

from casestudy.models import Security
from casestudy import securities_client

app = Celery()
dt = datetime.utcnow()
market_open = dt.replace(hour=14, minute=30, second=0, microsecond=0)
market_close = dt.replace(hour=21, minute=0, second=0, microsecond=0)

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(5.0, update_security_prices)

    # sender.add_periodic_task(
    #     crontab(minute='30',
    #             hour='14',
    #             day_of_week='mon-fri')
    # )

@shared_task()
def update_security_prices(force):
    print('update security prices')
    now = datetime.utcnow()
    today = datetime.today()
    if (0 <= today.weekday() <= 4 and market_open.time() <= now.time() <= market_close.time()) or force:
        #do the update
        securities = Security.objects.all()
        ticker_names = []
        for sec in securities:
            ticker_names.append(sec.ticker)
        prices = securities_client.get_prices(ticker_names)
        for sec in securities:
            sec.last_price = prices[sec.ticker]
        Security.objects.bulk_update(securities, ['last_price'])



@shared_task()
def update_available_securities():
    #stuff
    print('update available securities')
    securities_json = securities_client.get_tickers()
    securities = []
    for key, value in securities_json.items():
        securities.append(Security(ticker=key, name=value))
    
    Security.objects.bulk_create(
        securities,
        update_conflicts=True,
        update_fields=['ticker', 'name'],
        unique_fields=['ticker'])

@worker_ready.connect
def at_start(sender, **k):
    print('running starting task')
    update_available_securities()
    update_security_prices(True)