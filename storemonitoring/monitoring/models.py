from django.db import models
import pytz


class DayOfWeek(models.IntegerChoices):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Store(models.Model):
    store_id = models.PositiveBigIntegerField(primary_key=True)
    timezone = models.CharField(
        max_length=max(len(tz) for tz in pytz.all_timezones),
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default='America/Chicago'
    )

    def __str__(self) -> str:
        return str(self.store_id)


class Schedule(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day_of_week = models.PositiveSmallIntegerField(choices=DayOfWeek.choices)
    start_time = models.DateTimeField()     ## Local time
    end_time = models.DateTimeField()       ## Local time

    def __str__(self) -> str:
        return f"{self.store}@{self.day_of_week}"