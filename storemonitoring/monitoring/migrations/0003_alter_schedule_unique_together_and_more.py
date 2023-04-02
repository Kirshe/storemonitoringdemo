# Generated by Django 4.1.7 on 2023-04-02 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0002_remove_store_day_of_week_remove_store_end_time_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='schedule',
            unique_together={('store', 'day_of_week', 'start_time', 'end_time')},
        ),
        migrations.AlterUniqueTogether(
            name='store',
            unique_together={('store_id', 'timezone')},
        ),
    ]