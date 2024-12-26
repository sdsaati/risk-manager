from django.contrib import admin
from trade.models import Broker, Trade, User, UserBroker, Symbol
# Register your models here.


@admin.register(Broker)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


@admin.register(Trade)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('ub', 'result', 'amount')


@admin.register(UserBroker)
class MyModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Symbol)
class MyModelAdmin(admin.ModelAdmin):
    pass
