from django.db.utils import IntegrityError
from .models import Store, Schedule, DayOfWeek
import csv
import datetime
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