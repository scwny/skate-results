# Generated by Django 4.2.20 on 2025-05-09 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_event_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='enterAt',
            field=models.CharField(blank=True, help_text='Lobby if suffix ‘L’, Zamboni if suffix ‘Z’', max_length=20, null=True),
        ),
    ]
