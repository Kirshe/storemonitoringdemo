import datetime
from io import StringIO
from typing import List
from django.db.utils import IntegrityError
from celery import shared_task

from storemonitoring.monitoring.report import ReportGenerator
from .models import Report, Status, Store, Schedule, DayOfWeek, UpDownTime
import csv
import pytz
import requests
import logging


def read_stores_csv(filename: str):
    with open(filename, 'r') as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            Store.objects.update_or_create(
                store_id=row['store_id'],
                defaults=dict(
                    timezone=row['timezone_str']
                )
            )


def read_schedule_csv(filename: str):
    with open(filename, 'r') as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            store, _ = Store.objects.get_or_create(store_id=row['store_id'])
            try:
                Schedule.objects.create(
                    store=store,
                    day_of_week=DayOfWeek(int(row['day'])),
                    start_time=row['start_time_local'],
                    end_time=row['end_time_local']
                )
            except IntegrityError as ex:
                logging.error(
                    f"Error in saving schedule {row}. Maybe already exists", 
                    exc_info=ex
                )


@shared_task
def status_csv_poll(url: str):
    res = requests.get(url)
    if not res.ok:
        raise Exception("status fetch failed")
    csv_data = res.text.splitlines()
    reader = csv.DictReader(csv_data)
    for row in reader:
        store = Store.objects.filter(store_id=row['store_id']).get()
        utc_timestamp = datetime.datetime.strptime(row['timestamp_utc'], "%Y-%m-%d %H:%M:%s UTC")
        timestamp = pytz.utc.localize(utc_timestamp, is_dst=None).astimezone(pytz.timezone(store.timezone))
        schedules: List[Schedule] = store.schedule_set.filter(day_of_week=DayOfWeek(timestamp.weekday()))
        if not schedules:
            schedules = [Schedule(
                store=store, 
                day_of_week=DayOfWeek(timestamp.weekday()), 
                start_time=datetime.time(0, 0, 0), 
                end_time=datetime.time(23, 59, 59)
            )]
        if any((schedule.start_time <= timestamp.time() <= schedule.end_time) for schedule in schedules):
            status_expected = Status.UP
        else:
            status_expected = Status.DOWN
        status = Status.UP if row['status'] == 'active' else Status.DOWN
        UpDownTime.objects.create(
            store=store,
            timestamp=utc_timestamp,
            status_expected=status_expected,
            status=status
        )


@shared_task
def generate_report(report: Report):
    fp = StringIO()
    writer = csv.writer(fp)
    header = [
        "store_id", "uptime_last_hour(in minutes)", "uptime_last_day(in hours)", 
        "update_last_week(in hours)", "downtime_last_hour(in minutes)", "downtime_last_day(in hours)", 
        "downtime_last_week(in hours)"
    ]
    writer.writerow(header)
    for store in Store.objects.all():
        report_generator = ReportGenerator(store)
        uptime_hour, downtime_hour = report_generator.uptime_last_hour()
        uptime_day, downtime_day = report_generator.uptime_last_day()
        uptime_week, downtime_week = report_generator.uptime_last_week()
        writer.writerow([
            store.store_id,
            uptime_hour.total_seconds() // 60,
            uptime_day.total_seconds() // 3600,
            uptime_week.total_seconds() // 3600,
            downtime_hour.total_seconds() // 60,
            downtime_day.total_seconds() // 3600,
            downtime_week.total_seconds() // 3600
        ])
    fp.seek(0)
    report.csv = fp.read()
    report.generated = True
    report.save()