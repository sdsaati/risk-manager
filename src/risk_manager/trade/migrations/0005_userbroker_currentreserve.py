# Generated by Django 5.1.1 on 2024-10-14 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trade", "0004_alter_usersymbol_strategy_alter_usersymbol_timeframe"),
    ]

    operations = [
        migrations.AddField(
            model_name="userbroker",
            name="currentReserve",
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
