from django.contrib import admin
from trade.models import Broker, UserSymbol, User, UserBroker, Symbol
# Register your models here.


@admin.register(Broker)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


@admin.register(UserSymbol)
class MyModelAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)


@admin.register(UserBroker)
class MyModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Symbol)
class MyModelAdmin(admin.ModelAdmin):
    pass
