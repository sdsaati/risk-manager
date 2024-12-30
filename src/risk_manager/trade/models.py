"""_summary_

    all of the model classes are here
    we should use makemigrate command to create migration queries
    and the by migrate command we can apply those queries
"""

# import uuid
# for setting the default floating point of Decimals
# from copy import deepcopy
from decimal import Decimal as d
from decimal import getcontext

from django.contrib.auth.models import User
from django.db import models
from icecream import ic


class Broker(models.Model):
    """broker name and its default commission

    Args:
        models (_type_): _description_
    """

    # id = models.UUIDField(primary_key=True,
    #                       default=uuid.uuid4, editable=False)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    defaultCommission = models.DecimalField(max_digits=15,
                                            decimal_places=4,
                                            default=d("0.0"))

    def __str__(self):
        getcontext().prec = 4
        return self.name + " with " + str(self.defaultCommission)
        + " Commission"


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
    commission = models.DecimalField(max_digits=15,
                                     decimal_places=4,
                                     default=d("0.0"))

    def __str__(self):
        getcontext().prec = 4
        return f"{self.name}({d(self.commission)})"


class UserBroker(models.Model):
    """account information of the user in a broker will be stored here

    Args:
        models (_type_): _description_
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)

    # the whole balance that a user has in a broker
    balance = models.DecimalField(max_digits=15,
                                  decimal_places=4,
                                  default=d(2000.0000))

    # current reserve that we can take our risk from
    reserve = models.DecimalField(max_digits=15,
                                  decimal_places=4,
                                  default=d(1800.0000))
    # with this we can compute definedReserve by using the balance of user
    reservePercent = models.DecimalField(max_digits=15,
                                         decimal_places=4,
                                         default=10.0000)
    # with this we can compute risk for each trade
    # by using available balance for trading
    riskPercent = models.DecimalField(max_digits=15,
                                      decimal_places=4,
                                      default=1.0000)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username + " in " + self.broker.name

    @property
    def defined_reserve(self):
        return (self.reservePercent * self.balance) / d(100)

    @property
    def available_balance(self):
        return self.balance - self.defined_reserve

    def reserve_is_empty_update_balance(self):
        """if you loss so that you don't have any reserve anymore,
        here we update the balance of user, and compute the new
        reserve, risk, and available balance, ...

        Returns:
            d: this is the new reserve that this method will return
        """
        self.balance = self.available_balance
        self.reserve = self.defined_reserve
        # self.save()


class Trade(models.Model):
    """Trade table = Third table between users and symbols

    Args:
        models (_type_): _description_
    """

    id = models.AutoField(primary_key=True)
    ub = models.ForeignKey(UserBroker, on_delete=models.CASCADE)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(auto_now=True, null=True, blank=True)
    stop = models.DecimalField(max_digits=15, decimal_places=4)
    entry = models.DecimalField(max_digits=15, decimal_places=4)
    target = models.DecimalField(max_digits=15, decimal_places=4)
    # This will be a computational property
    #    riskReward = models.DecimalField(max_digits=15,
    #                                     decimal_places=4,
    #                                     default=d("1.0"))
    result = models.BooleanField(null=True, blank=True, default=None)
    result_amount = models.DecimalField(null=True,
                                        blank=True,
                                        max_digits=15,
                                        decimal_places=4,
                                        default=None)
    amount = models.DecimalField(max_digits=15, decimal_places=4)
    picture = models.CharField(max_length=500,
                               null=True,
                               blank=True,
                               default="")
    comment = models.TextField(null=True, blank=True, default="")
    isPositionChanged = models.BooleanField(default=False)
    timeFrame = models.CharField(max_length=400,
                                 null=True,
                                 blank=True,
                                 default="")
    strategy = models.CharField(max_length=500,
                                null=True,
                                blank=True,
                                default="")

    # Methods (Services of this model)
    def ub_id(self):
        return self.ub.id

    def balance(self):
        return self.ub.balance

    def reserve(self):
        return self.ub.reserve

    def __str__(self):
        return self.__dict__.__str__()

    def update_reserve_and_balance(self, save=True, result=None):
        """Compute the new balance [and/or] reserve
        with the result of the last trade
        NOTE: for trade we only use available balance!!!!!
        NOTE: self.amount also needs to be updated for next trade
        """

        getcontext().prec = 4

        # proposition calculuses:
        p: bool = (self.profit(result) > 0)  # our trade was a win
        q: bool = (self.ub.reserve
                   < self.ub.defined_reserve)  # our reserve isn't full
        z: bool = (self.ub.reserve
                   > self.risk)  # we have a bit reserve for a loss

        # if our reserve isn't full and we made a profit or we loss but have a bit reserve
        if (p and q) or ((not p) and z):
            self.ub.reserve = self.ub.reserve + self.profit(result)
            self.ub.balance = self.ub.balance
            ic("we are in first cond", p, q, z, self.ub.reserve,
               self.ub.defined_reserve)

        # if we did a profit but our reserve is full
        if (p and (not q)):
            self.ub.balance = self.ub.balance + (
                self.ub.reserve -
                self.ub.defined_reserve) + self.profit(result)
            self.ub.reserve = self.ub.defined_reserve  # now reset the reserve
            ic("we are in second cond", p, q, self.ub.reserve,
               self.ub.defined_reserve)

        # there is no reserve at all and we did a loss
        if ((not p) and (not z)):
            # need to compute again our risk, then with it compute
            # definedReserve
            self.ub.reserve_is_empty_update_balance()
            self.update_reserve_and_balance(result=result)
            ic("we are in third cond", p, z, self.ub.reserve,
               self.ub.defined_reserve)

        if save:
            pass
            # FIXME: which one is correct?
            # or does we even need this?
            ic(self.ub.balance)
            self.ub.save()
            # self.save()

    @property
    def risk_reward(self) -> d:
        if self.result:
            return (self.target - self.entry) / (self.entry - self.stop)
        else:
            return -((self.target - self.entry) / (self.entry - self.stop))

    @property
    def stop_percent(self) -> d:
        return ((self.entry - self.stop) / self.entry) * d(100)

    @property
    def commission(self) -> d:
        if self.symbol.commission is None:
            return self.ub.broker.defaultCommission
        else:
            return self.symbol.commission

    @property
    def amount_per_trade(self) -> d:
        return self.risk / ((self.stop_percent + self.commission) / d(100))

    @property
    def risk(self) -> d:
        return d(self.ub.riskPercent) * self.ub.available_balance / d(100)

    def profit(self, result=None):
        getcontext().prec = 4
        if result is not None:
            res = result
        else:
            res = self.result
        if res:
            return (self.ub.available_balance * (self.stop_percent / d(100)) *
                    self.risk_reward)
            -(self.ub.available_balance * (self.commission / d(100)))
        else:
            return -((self.ub.available_balance *
                      (self.stop_percent / d(100))) -
                     (self.ub.available_balance * (self.commission / d(100))))

    def cascade_update_reserve_and_balances(self, modified_row_id):
        pass

    class Meta:
        db_table = 'trade_usersbrokersymbol'
