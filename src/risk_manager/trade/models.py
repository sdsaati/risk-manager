"""_summary_

    all of the model classes are here
    we should use makemigrate command to create migration queries
    and the by migrate command we can apply those queries
"""

import uuid
from django.db import models
from django.contrib.auth.models import User

# from copy import deepcopy
from decimal import Decimal as d

# for setting the default floating point of Decimals
from decimal import getcontext


class Broker(models.Model):
    """broker name and its default commision

    Args:
        models (_type_): _description_
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    defaultCommission = models.DecimalField(
        max_digits=15, decimal_places=4, default=d("0.0")
    )

    def __str__(self):
        getcontext().prec = 4
        return self.name + " with " + str(self.defaultCommission)
        +" Commission"


class Symbol(models.Model):
    """symbols that a broker may have stored here

    Args:
        models (_type_): _description_
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    # if this is null, then we must use the
    # Broker.defaultCommission value for this field
    commission = models.DecimalField(max_digits=15, decimal_places=4, default=d("0.0"))

    def __str__(self):
        getcontext().prec = 4
        return f"{self.name}({d(self.commission)})"


class UserSymbol(models.Model):
    """Trade table = Third table between users and symbols

    Args:
        models (_type_): _description_
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(auto_now=True, null=True, blank=True)
    result = models.BooleanField(null=True, blank=True, default=None)
    entry = models.DecimalField(max_digits=15, decimal_places=4)
    amount = models.DecimalField(max_digits=15, decimal_places=4)
    target = models.DecimalField(max_digits=15, decimal_places=4)
    stop = models.DecimalField(max_digits=15, decimal_places=4)
    riskReward = models.DecimalField(max_digits=15, decimal_places=4, default=d("1.0"))
    picture = models.CharField(max_length=500, null=True, blank=True, default="")
    comment = models.TextField(null=True, blank=True, default="")
    isPositionChanged = models.BooleanField(default=False)
    timeFrame = models.CharField(max_length=400, null=True, blank=True, default="")
    strategy = models.CharField(max_length=500, null=True, blank=True, default="")

    # Methods (Services of this model)

    def __str__(self):
        ub = self.getUserBroker()
        separator = "\n"
        return f"""{separator}-------------------------------------------------
            {separator}username is '{self.user.username}' and boroker
            is '{self.symbol.broker.name}' on symbol '{self.symbol.name}'
            with entry of '{self.entry}' and stop of '{self.stop}' and target
            is '{self.target}', now RR is computed as '{self.risk_reward()}'.
            {separator}we did '{self.profit()}' profit/loss{separator}
            current reserve is '{ub.reserve}' and available
            balance is '{ub.getAvailableBalance()}' and balance is '{ub.balance}'
            {separator}trade done at '{self.date}'
            {separator}-------------------------------------------------"""

    def entryAmountCompute(self):
        """Compute the new balance [and/or] reserve
        with the result of the last trade
        NOTE: for trade we only use available balance!!!!!
        NOTE: self.amount also needs to be updated for next trade
        """

        getcontext().prec = 4
        ub = self.getUserBroker()
        definedReserve = ub.getDefinedReserve()
        risk = ub.getRisk()
        profit = self.profit()

        if profit > 0:  # we did profit
            if ub.reserve < definedReserve:  # reserve is not full
                ub.reserve = ub.reserve + profit
            else:  # reserve is full
                ub.balance = ub.balance + (ub.reserve - definedReserve) + profit
                ub.reserve = definedReserve  # now reset the reserve
        else:  # we did loss
            if ub.reserve > risk:  # still there are some reserve
                ub.reserve = ub.reserve + profit  # we take our loss from reserve
            else:  # there is no reserve at all
                # need to compute again our risk, then with it compute
                # definedReserve
                ub.reserveIsEmptyUpdateBalance()
                self.entryAmountCompute()

        ub.save()

    def getUserBroker(self):
        ub = UserBroker.objects.get(broker=self.symbol.broker, user=self.user)
        return ub

    def risk_reward(self):
        if self.result:
            return (self.target - self.entry) / (self.entry - self.stop)
        else:
            return -((self.target - self.entry) / (self.entry - self.stop))

    def stop_percent(self):
        return ((self.entry - self.stop) / self.entry) * d(100)

    def getCommission(self) -> d:
        ub = self.getUserBroker()
        if self.symbol.commission is None:
            return ub.broker.defaultCommission
        else:
            return self.symbol.commission

    def getAmountPerTrade(self):
        ub = self.getUserBroker()
        return ub.getRisk() / ((self.stop_percent() + self.getCommission()) / d(100))

    def profit(self):
        ub = self.getUserBroker()
        getcontext().prec = 4
        if self.result:
            return (
                ub.getAvailableBalance()
                * (self.stop_percent() / d(100))
                * self.risk_reward()
            )
            -(ub.getAvailableBalance() * (self.getCommission() / d(100)))
        else:
            return -(
                (ub.getAvailableBalance() * (self.stop_percent() / d(100)))
                - (ub.getAvailableBalance() * (self.getCommission() / d(100)))
            )


class UserBroker(models.Model):
    """account information of the user in a broker will be stored here

    Args:
        models (_type_): _description_
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)

    # the whole balance that a user has in a broker
    balance = models.DecimalField(max_digits=15, decimal_places=4)
    # current reserve that we can take our risk from
    reserve = models.DecimalField(max_digits=15, decimal_places=4)
    # with this we can compute definedReserve by using the balance of user
    reservePercent = models.DecimalField(max_digits=15, decimal_places=4, default=10.0000)
    # with this we can compute risk for each trade by using available balance for trading
    riskPercent = models.DecimalField(max_digits=15, decimal_places=4)

    def __str__(self):
        return self.user.username + " in " + self.broker.name

    def getDefinedReserve(self):
        return self.reservePercent * self.balance / d(100)

    def getAvailableBalance(self):
        return self.balance - self.getDefinedReserve()

    def getRisk(self) -> d:
        return (d(self.riskPercent) / d(100)) * self.getAvailableBalance()

    def reserveIsEmptyUpdateBalance(self):
        """if you loss so that you don't have any reserve anymore,
        here we update the balance of user, and compute the new
        reserve, risk, and available balance, ...

        Returns:
            d: this is the new reserve that this method will return
        """
        self.balance = self.getAvailableBalance()
        self.reserve = self.getDefinedReserve()
        self.save()
