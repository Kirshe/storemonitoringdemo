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


class Status(models.TextChoices):
    UP = "UP"
    DOWN = "DOWN"


class Store(models.Model):
    store_id = models.PositiveBigIntegerField(primary_key=True)
    timezone = models.CharField(
        max_length=max(len(tz) for tz in pytz.all_timezones),
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default='America/Chicago'
    )

    class Meta:
        unique_together = ('store_id', 'timezone')

    def __str__(self) -> str:
        return str(self.store_id)


class Schedule(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day_of_week = models.PositiveSmallIntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()     ## Local time
    end_time = models.TimeField()       ## Local time

    class Meta:
        unique_together = ('store', 'day_of_week', 'start_time', 'end_time')

    def __str__(self) -> str:
        return f"{self.store}@{self.day_of_week}"


class UpDownTime(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    status = models.CharField(max_length=4, choices=Status.choices)
    timestamp = models.DateTimeField()  ## UTC time


class Report(models.Model):
    csv = models.TextField(null=True, default=None)
    generated = models.BooleanField(default=False)