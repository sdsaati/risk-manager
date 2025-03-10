from django.contrib import admin
from trade.models import Broker, Trade, User, UserBroker, Symbol

# Register your models here. and say which fields of them shuold be displayed in admin pages


@admin.register(Broker)
class MyModelAdmin(admin.ModelAdmin):  # type:ignore
    list_display = (
        "name",
        "id",
    )


@admin.register(Trade)
class MyModelAdmin(admin.ModelAdmin):  # type:ignore
    list_display = (
        "id",
        "ub",
        "ub_id",
        "result",
        "amount",
        "balance",
        "reserve",
    )


@admin.register(UserBroker)
class MyModelAdmin(admin.ModelAdmin):  # type:ignore
    list_display = (
        "id",
        "balance",
        "reserve",
        "user_id",
        "broker",
        "broker_id",
    )


@admin.register(Symbol)
class MyModelAdmin(admin.ModelAdmin):  # type:ignore
    list_display = (
        "name",
        "id",
        "commission",
    )
