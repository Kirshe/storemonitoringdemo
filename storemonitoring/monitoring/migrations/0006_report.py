# Generated by Django 4.1.7 on 2023-04-03 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0005_updowntime'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csv', models.TextField(default=None, null=True)),
            ],
        ),
    ]
