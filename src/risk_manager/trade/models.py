"""_summary_

    all of the model classes are here
    we should use makemigrate command to create migration queries
    and the by migrate command we can apply those queries
"""

import uuid
from django.db import models
from django.contrib.auth.models import User


class Broker(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    defaultCommission = models.FloatField(default=0.0)


class Symbol(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    # if this is null, then we must use the
    # Broker.defaultCommission value for this field
    commission = models.FloatField()


class UserSymbol(models.Model):
    """ Third table between users and symbols = Trade Table.

    Args:
        models (_type_): _description_
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    result = models.BooleanField(null=True, blank=True)
    entry = models.FloatField()
    amount = models.FloatField()
    target = models.FloatField()
    stop = models.FloatField()
    riskReward = models.PositiveIntegerField()
    picture = models.CharField(max_length=500, null=True, default="")
    comment = models.TextField(null=True)
    isPositionChanged = models.BooleanField(default=False)
    timeFrame = models.CharField(max_length=400, null=True)
    strategy = models.CharField(max_length=500, null=True)


class UserBroker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    balance = models.FloatField()
    reserve = models.FloatField()
    riskPercent = models.FloatField(default=10.0)
