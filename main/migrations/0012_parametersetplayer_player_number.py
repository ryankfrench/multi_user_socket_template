# Generated by Django 4.1.3 on 2022-11-22 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_parameterset_json_for_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersetplayer',
            name='player_number',
            field=models.IntegerField(default=0, verbose_name='Player number'),
        ),
    ]
