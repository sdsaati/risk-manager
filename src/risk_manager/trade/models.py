"""_summary_

    all of the model classes are here
    we should use makemigrate command to create migration queries
    and the by migrate command we can apply those queries
"""

# Delays evaluation of type hints until runtime
from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from decimal import Decimal as d
from decimal import getcontext

# import uuid
# for setting the default floating point of Decimals
# from copy import deepcopy
from typing import Any

from django.contrib.auth.models import User
from django.db import models, transaction
from icecream import ic

logger = logging.getLogger("django")
getcontext().prec = 4


class Broker(models.Model):
    """broker name and its default commission

    Args:
        models (_type_): _description_
    """

    # id = models.UUIDField(primary_key=True,
    #                       default=uuid.uuid4, editable=False)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    defaultCommission = models.DecimalField(
        max_digits=15, decimal_places=4, default=d("0.0")
    )

    def __str__(self):
        return self.name + " with " + str(self.defaultCommission)
        +" Commission"


class Symbol(models.Model):
    """symbols that a broker may have stored here

    Args:
        models (_type_): _description_
    """

    id = models.AutoField(primary_key=True)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    # if this is null, then we must use the
    # Broker.defaultCommission value for this field
    commission = models.DecimalField(
        max_digits=15, decimal_places=4, blank=True, null=True
    )

    def __str__(self):
        if self.commission is not None:
            return f"{self.name}({d(self.commission)})"
        else:
            return f"{self.name}"


class UserBroker(models.Model):
    """account information of the user in a broker will be stored here

    Args:
        models (_type_): _description_
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)

    # the whole balance that a user has in a broker
    balance = models.DecimalField(
        max_digits=15, decimal_places=4, default=d(0))

    # current reserve that we can take our risk from
    reserve = models.DecimalField(
        max_digits=15, decimal_places=4, default=d(0))
    # with this we can compute definedReserve by using the balance of user
    reservePercent = models.DecimalField(
        max_digits=15, decimal_places=4, default=d(0))
    # with this we can compute risk for each trade
    # by using available balance for trading
    riskPercent = models.DecimalField(
        max_digits=15, decimal_places=4, default=d(0))

    def __str__(self):
        return self.user.username + " in " + self.broker.name

    @property
    def defined_reserve(self):
        return (self.reservePercent * self.balance) / d(100)

    @property
    def available_balance(self):
        return self.balance - self.defined_reserve

    @property
    def risk(self) -> d:
        return d(self.riskPercent) * self.available_balance / d(100)

    def reserve_is_empty_update_balance(self):
        """if you loss so that you don't have any reserve anymore,
        here we update the balance of user, and compute the new
        reserve, risk, and available balance, ...

        Returns:
            d: this is the new reserve that this method will return
        """
        self.balance = self.available_balance
        self.reserve = self.defined_reserve
        # NOTE: We don't need to save this because inside the
        # signal, we save ub(this object) too
        # self.save()


class StopAndRiskrewardStrategy(ABC):
    """
    IMPORTANT! This is not a Model
    This is strategy (design) pattern that let we choose
    wether we should compute risk reward ratio and stop loss percentage from entry, stop, and targets from user inputs
    or get it directly from user inputs
    """

    @abstractmethod
    def get_risk_reward(self) -> d:
        raise NotImplementedError()

    @abstractmethod
    def get_stop_percentage(self) -> d:
        raise NotImplementedError()


class ComputeRRandSLP(StopAndRiskrewardStrategy):
    """
    IMPORTANT! This is not a Model
    This class is a concrete class that is part of strategy pattern
    it can compute risk_reward_ratio and stop_loss_percentage by entry, stop and target
    """

    def __init__(self, entry: d, stop: d, target: d, result: bool | None = None):
        self.entry: d = entry
        self.stop: d = stop
        self.target: d = target
        self.result: bool | None = result

    def risk_reward(self) -> d:
        if self.result:
            return (self.target - self.entry) / (self.entry - self.stop)
        else:
            return -((self.target - self.entry) / (self.entry - self.stop))

    def stop_percent(self) -> d:
        return ((self.entry - self.stop) / self.entry) * d(100)

    def get_risk_reward(self) -> d:
        return self.risk_reward()

    def get_stop_percentage(self) -> d:
        return self.stop_percent()


class GetRRandSLP(StopAndRiskrewardStrategy):
    """
    IMPORTANT! This is not a Model
    This class is a concrete class that is part of strategy pattern
    it can return risk_reward_ratio and stop_loss_percentage that user gave us
    """

    def __init__(self, risk_reward: d, stop_percent: d):
        self.risk_reward: d = risk_reward
        self.stop_percent: d = stop_percent

    def get_risk_reward(self) -> d:
        return self.risk_reward

    def get_stop_percentage(self) -> d:
        return self.stop_percent


class RR_Stop_Factory:
    def create(
        self,
        entry=None,
        stop=None,
        target=None,
        risk_reward=None,
        stop_percentage=None,
        result=None,
    ) -> StopAndRiskrewardStrategy:
        if entry is not None and stop is not None and target is not None:
            return ComputeRRandSLP(entry=entry, stop=stop, target=target, result=result)
        elif stop_percentage is not None and risk_reward is not None:
            return GetRRandSLP(stop_percent=stop_percentage, risk_reward=risk_reward)
        else:
            raise ValueError(
                "You need to provide (entry, stop, target) or (risk_reward, stop_percentage)"
            )


class Trade(models.Model):
    """Trade table = Third table between users and symbols

    Args:
        models (_type_): _description_
    """

    id = models.AutoField(primary_key=True)
    ub: UserBroker = models.ForeignKey(UserBroker, on_delete=models.CASCADE)
    symbol: Symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(auto_now=True, null=True, blank=True)
    stop = models.DecimalField(
        max_digits=25, decimal_places=4, null=True, blank=True)
    entry = models.DecimalField(
        max_digits=25, decimal_places=4, null=True, blank=True)
    target = models.DecimalField(
        max_digits=25, decimal_places=4, null=True, blank=True)
    # This will be a computational property
    #    riskReward = models.DecimalField(max_digits=25,
    #                                     decimal_places=4,
    #                                     default=d("1.0"))
    result = models.BooleanField(null=True, blank=True, default=None)
    result_amount = models.DecimalField(
        null=True, blank=True, max_digits=25, decimal_places=4, default=None
    )
    amount = models.DecimalField(
        max_digits=25, decimal_places=4, null=True, blank=True)
    picture = models.CharField(
        max_length=500, null=True, blank=True, default="")
    comment = models.TextField(null=True, blank=True, default="")
    isPositionChanged = models.BooleanField(default=False)
    timeFrame = models.CharField(
        max_length=400, null=True, blank=True, default="")
    strategy = models.CharField(
        max_length=500, null=True, blank=True, default="")
    risk_reward = models.DecimalField(
        null=True, blank=True, max_digits=25, decimal_places=4, default=None
    )
    stop_percent = models.DecimalField(
        null=True, blank=True, max_digits=25, decimal_places=4, default=None
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.warn(
            f"we saved ub: {str(self.ub.id)} with this balance: {
                str(self.ub.balance)}"
        )

    # Methods (Services of this model)
    def ub_id(self):
        return self.ub.id

    def balance(self):
        return self.ub.balance

    def reserve(self):
        return self.ub.reserve

    def check_reserve_overflow(self):
        """
        If reserve has a value above of defined reserve, then
        it need to be set to defined reserve, and delta added to balance
        """
        if self.ub.reserve > self.ub.defined_reserve:
            self.ub.balance = self.ub.balance + (
                self.ub.reserve - self.ub.defined_reserve
            )
            self.ub.reserve = self.ub.defined_reserve

    def __str__(self):
        return self.__dict__.__str__()

    def update_reserve_and_balance(
        self,
        save=False,
        result: bool | None = None,
        previews_trade_balance: d | None = None,
        previews_trade_reserve: d | None = None,
    ) -> None:
        """Compute the new balance [and/or] reserve
        with the result of the last trade
        NOTE: for trade we only use available balance!!!!!
        NOTE: self.amount also needs to be updated for next trade
        """

        if previews_trade_balance is not None:
            self.ub.balance = previews_trade_balance
        if previews_trade_reserve is not None:
            self.ub.reserve = previews_trade_reserve

        # proposition calculuses:
        p: bool = self.profit(result) > 0  # our trade was a win
        q: bool = self.ub.reserve < self.ub.defined_reserve  # our reserve isn't full
        z: bool = self.ub.reserve > self.risk  # we have a bit reserve for a loss

        # if our reserve isn't full and we made a profit or we loss but have a bit reserve
        if (p and q) or ((not p) and z):
            self.ub.reserve = self.ub.reserve + self.profit(result)
            self.check_reserve_overflow()
            # self.ub.balance = self.ub.balance
            ic(
                "we are in first cond",
                p,
                q,
                z,
                self.ub.reserve,
                self.ub.defined_reserve,
            )

        # if we did a profit but our reserve is full
        if p and (not q):
            self.ub.balance = (
                self.ub.balance
                + (self.ub.reserve - self.ub.defined_reserve)
                + self.profit(result)
            )
            self.ub.reserve = self.ub.defined_reserve  # now reset the reserve
            ic("we are in second cond", p, q,
               self.ub.reserve, self.ub.defined_reserve)

        # there is no reserve at all and we did a loss
        if (not p) and (not z):
            # need to compute again our risk, then with it compute
            # definedReserve
            self.ub.reserve_is_empty_update_balance()
            self.update_reserve_and_balance(result=result)
            ic("we are in third cond", p, z,
               self.ub.reserve, self.ub.defined_reserve)

        if save == True:
            with transaction.atomic():
                self.ub.save()
                self.ub.user.save()
                self.ub.broker.save()
                self.symbol.save()
                self.symbol.broker.save()

    @property
    def commission(self) -> d:
        if self.symbol.commission is None:
            return self.ub.broker.defaultCommission
        else:
            return self.symbol.commission

    # NOTE: this method isn't used almost anywhere
    @property
    def amount_per_trade(self) -> d:
        return self.risk / ((self.stop_percent / d(100)) + self.commission)

    @property
    def risk(self) -> d:
        return d(self.ub.riskPercent) * self.ub.available_balance / d(100)

    def profit(self, result: bool | None = None) -> d:
        res = None
        if result is not None:
            res = result
        else:
            res = self.result
        if res:
            return (
                self.amount
                * (self.stop_percent / d(100))
                * self.risk_reward
            )
            -(self.amount * self.commission)
        else:
            return -(
                (self.amount * (self.stop_percent / d(100)))
                - (self.amount * self.commission)
            )

    class Meta:
        db_table = "trade_usersbrokersymbol"
