# from django.db.models.signals import post_save  # the actual signal
import logging

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models.signals import pre_save  # the actual signal
from django.dispatch import receiver  # decorator for connecting signal
from icecream import ic
from trade.models import Trade
from trade.trade_states import *

logger = logging.getLogger("django")

# @receiver(post_save, sender=UserSymbol)
# def on_result_changed(sender, instance: UserSymbol, created, **kwargs):
#     """this call whenever an existing trade updated.
#
#     Args:
#         sender (_type_): the model class that emitted this signal
#         instance (UserSymbol): the actual record that is updated
#         created (_type_): is the record new or updated
#     """
#     if not created:  # if record is updated (not created)
#         print(instance)
#         # if result is True or False (and not None)
#         if instance.result is not None:
#             instance.entryAmountCompute()
#         print(instance)


@receiver(pre_save, sender=Trade)
def check_balance_is_changed(sender: Trade, instance: Trade, **kwargs):
    """this event will check if result of a trade is changed or not.
    if it's changed, we must update other fields like reserve, definedReserve
    and risk, riskReward, AvailableBalance

    Args:
        sender (_type_): is the model class (our table)
        instance (_type_): is an object of class (our row=record)
    """
    if instance.pk:  # Ensure if record is edited(It's not new pk=None)
        # ic("we are editing the trade: ", instance.pk)

        # NOTE:
        # To Fetch the record before the edit:
        # original = sender.objects.get(pk=instance.pk)
        # if original.result != instance.result:
        try:
            before_edit: Trade | None = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            before_edit = None

        # (1) Check to see if any of these fields are edited in admin page
        if before_edit is not None and (
            (before_edit.stop != instance.stop)
            or (before_edit.entry != instance.entry)
            or (before_edit.target != instance.target)
            or (before_edit.amount != instance.amount)
            or (before_edit.result != instance.result)
            or (before_edit.ub.reserve != instance.reserve)
            or (before_edit.balance != instance.balance)
        ):
            ic(
                "BEFORE:",
                before_edit.ub.balance,
                before_edit.ub.reserve,
                before_edit.amount,
            )
            tsm = TradeStateManager(instance, before_edit, sender)
            with transaction.atomic():
                instance.ub.save()
                instance.ub.user.save()
                instance.ub.broker.save()
                instance.symbol.save()
                instance.symbol.broker.save()
                ic("AFTER:", instance.ub.balance, instance.ub.reserve, instance.amount)
