"""Routes of the trade application are defined here"""

from django.urls import path
from trade import views

urlpatterns = [
    path("", views.index),
    path("new/", views.new, name="new_trade"),  # form of new trade
    path("new/<str:status>/", views.new, name="new_trade_with_status"),  # db response
    path(
        "balance/", views.balance, name="addremove_balance"
    ),  # add/remove balance form
    path(
        "balance/<str:status>/", views.balance, name="addremove_balance_with_status"
    ),  # db response
    path("balance-commit/", views.balance_commit, name="balance_commit"),
    path("new-commit/", views.new_commit, name="new_trade_commit"),  # saving into db
    path("api_all/", views.api_all, name="api_all"),
]
