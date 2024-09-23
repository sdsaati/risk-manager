# Generated by Django 5.1.1 on 2024-09-22 10:50

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Broker",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("defaultCommission", models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Symbol",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "broker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="trade.broker"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserBroker",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("balance", models.FloatField()),
                ("reserve", models.FloatField()),
                ("riskPercent", models.FloatField(default=10.0)),
                (
                    "broker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="trade.broker"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="trade.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserSymbol",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date", models.DateTimeField()),
                ("result", models.BooleanField(blank=True, null=True)),
                ("entry", models.FloatField()),
                ("amount", models.FloatField()),
                ("target", models.FloatField()),
                ("stop", models.FloatField()),
                ("riskReward", models.PositiveIntegerField()),
                ("commission", models.FloatField(default=0.0)),
                ("picture", models.CharField(default="", max_length=500, null=True)),
                ("comment", models.TextField()),
                ("isPositionChanged", models.BooleanField(default=False)),
                ("timeFrame", models.CharField(max_length=400)),
                ("strategy", models.CharField(max_length=500)),
                (
                    "symbol",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="trade.symbol"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="trade.user"
                    ),
                ),
            ],
        ),
    ]