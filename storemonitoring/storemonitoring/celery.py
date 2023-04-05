import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storemonitoring.settings')

app = Celery('storemonitoring')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = "redis://localhost:6379/0"

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'status_check_every_hour': {
        'task': 'monitoring.tasks.status_csv_poll',
        'args': ("http://localhost:9000/storestatus.csv",),
        'schedule': crontab(hour='*')
    }
}