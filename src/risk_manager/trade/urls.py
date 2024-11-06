"""Routes of the trade application are defined here"""
from django.urls import path
from trade import views

urlpatterns = [
    path('', views.index),
    path('new/', views.new, name='new_trade'),  # form of new trade
    # response from the db
    path('new/<str:status>/', views.new, name='new_trade_with_status'),
    path('new-commit/', views.new_commit,
         name='new_trade_commit'),  # saving into db
    path('api_commission/', views.api_commission, name="api_commission"),
    path('api_risk/', views.api_risk, name="api_risk")
]
