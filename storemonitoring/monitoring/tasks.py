import datetime
from typing import List
from django.db.utils import IntegrityError
from .models import Store, Schedule, DayOfWeek, UpDownTime
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
                start_time="00:00:00", 
                end_time="00:00:00"
            )]
        for schedule in schedules:
            if schedule.start_time <= timestamp.time() <= schedule.end_time and row['status'] == 'active':
                logging.debug(f"Timestamp is as expected for {store}: {row}")
            else:
                status = UpDownTime.Status.UP if row['status'] == 'inactive' else UpDownTime.Status.DOWN
                UpDownTime.objects.create(
                    store=store,
                    timestamp=utc_timestamp,
                    status=status
                )

        