# from django.db.models.signals import post_save  # the actual signal
from django.db.models.signals import pre_save  # the actual signal
from django.dispatch import receiver  # decorator for connecting signal
from icecream import ic
from trade.models import Trade

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
        ic("we are editing the trade: ", instance.pk)

        # NOTE:
        # To Fetch the record before the edit:
        # original = sender.objects.get(pk=instance.pk)
        # if original.result != instance.result:
        before_edit_stop = sender.objects.get(pk=instance.pk)
        before_edit_entry = sender.objects.get(pk=instance.pk)
        before_edit_target = sender.objects.get(pk=instance.pk)
        before_edit_amount = sender.objects.get(pk=instance.pk)
        before_edit_result = sender.objects.get(pk=instance.pk)

        if (before_edit_stop
                != instance.stop) or (before_edit_entry != instance.entry) or (
                    before_edit_target != instance.target) or (
                        before_edit_amount
                        != instance.amount) or (before_edit_result
                                                != instance.result):
            if instance.result is not None:  # if new result is Yes or No
                instance.update_reserve_and_balance(instance.result)
                ic(instance.ub.balance)
