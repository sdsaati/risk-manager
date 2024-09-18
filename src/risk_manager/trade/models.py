"""_summary_
    all of the model classes are here
    we should use makemigrate command to create migration queries
    and the by migrate command we can apply those queries
"""

from django.db import models


class Broker(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    risk = models.FloatField()  # $ risk amount


class User(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    name = models.CharField(max_length=255)


class Symbol(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)


class Trade(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    r_r = models.PositiveIntegerField()  # R:R Ratio
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)


class UserBroker(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
