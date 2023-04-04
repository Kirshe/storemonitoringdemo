import datetime
from typing import List, Tuple

import pytz

from storemonitoring.monitoring.models import DayOfWeek, Schedule, Status, Store, UpDownTime


class ReportGenerator:

    def __init__(self, store: Store) -> None:
        self.now = datetime.datetime.utcnow().replace(microsecond=0)   ## Removing microsecond precision since data is not in microseconds
        self.store = store
        self.local_now = pytz.timezone(store.timezone).fromutc(self.now)
        self._runs_all_day = not Schedule.objects.filter(store=store).exists()

    def make_utc_time(self, timestamp: datetime.datetime) -> datetime.datetime:
        return pytz.timezone(self.store.timezone).localize(
            timestamp
        ).astimezone(pytz.utc).replace(tzinfo=None)
    
    def _uptime_calc(self, schedules: List[Schedule], date_func) -> Tuple[datetime.timedelta, datetime.timedelta]:
        up_times: List[Tuple[datetime.timedelta, Status]] = []
        for schedule in schedules:
            date = date_func(schedule)
            start_time = datetime.datetime.combine(date, schedule.start_time)
            end_time = datetime.datetime.combine(date, schedule.end_time)
            utc_start_time = self.make_utc_time(start_time)
            utc_end_time = self.make_utc_time(end_time)
            up_down_times = UpDownTime.objects.filter(
                store=self.store,
                timestamp__gte=utc_start_time,
                timestamp__lte=utc_end_time
            )
            down_start = None
            up_start = utc_start_time
            for up_down_time in up_down_times:
                if up_down_time.status == Status.DOWN and up_start:
                    down_start = up_down_time.timestamp
                    delta = down_start - up_start
                    up_times.append((delta, Status.UP))
                    up_start = None
                elif up_down_time.status == Status.UP and down_start:
                    up_start = up_down_time.timestamp
                    delta = up_start - down_start
                    up_times.append((delta, Status.DOWN))
                    down_start = None
            if down_start:
                delta = utc_end_time - down_start
                up_times.append((delta, Status.DOWN))
            elif up_start:
                delta = utc_end_time - up_start
                up_times.append((delta, Status.UP))
        total_uptime = sum(delta for delta, status in up_times if status == Status.UP)
        total_downtime = sum(delta for delta, status in up_times if status == Status.DOWN)
        return total_uptime, total_downtime

    def uptime_last_week(self):
        week_start = self.now.replace(
            day=(self.local_now.day - self.local_now.weekday()),
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        schedules = Schedule.objects.filter(
            store=self.store
        ).order_by('day_of_week', 'start_time', 'end_time')
        return self._uptime_calc(
            schedules, 
            lambda schedule: week_start.replace(
                day = week_start.day + schedule.day_of_week
            ).date()
        )

    def uptime_last_day(self):
        day_start = self.local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        schedules = Schedule.objects.filter(
            store=self.store,
            day_of_week=DayOfWeek(day_start.weekday())
        ).order_by('start_time', 'end_time')
        return self._uptime_calc(
            schedules,
            lambda _: day_start.date()
        )
    
    def uptime_last_hour(self):
        hour_start = self.local_now.replace(minute=0, second=0, microsecond=0)
        schedules = Schedule.objects.filter(
            store=self.store,
            day_of_week=DayOfWeek(hour_start.weekday()),
            start_time__gte=hour_start
        ).order_by('start_time', 'end_time')
        return self._uptime_calc(
            schedules,
            lambda _: hour_start.date()
        )
