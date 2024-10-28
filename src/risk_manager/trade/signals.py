# from django.db.models.signals import post_save  # the actual signal
from django.db.models.signals import pre_save  # the actual signal
from django.dispatch import receiver  # decorator for connecting signal
from trade.models import UserSymbol


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


@receiver(pre_save, sender=UserSymbol)
def check_balance_is_changed(sender: UserSymbol, instance: UserSymbol, **kwargs):
    """this event will check if result of a trade is changed or not.
    if it's changed, we must update other fields like reserve, definedReserve
    and risk, riskReward, AvailableBalance

    Args:
        sender (_type_): is the model class (our table)
        instance (_type_): is an object of class (our row=record)
    """
    if instance.pk:  # ensure if the balance is updated (it's not new)
        # Fetch the original instance from the database
        # original: UserSymbol = sender.objects.get(pk=instance.pk)
        # if original.result != instance.result:

        # Check if a specific field has changed
        if instance.result is not None:
            print(instance)
            instance.riskReward = instance.risk_reward()
            instance.entryAmountCompute()
            print(instance)
