from django.contrib import admin
from .models import Store, Schedule


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'timezone')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('store_id', 'day_of_week', 'start_time', 'end_time')