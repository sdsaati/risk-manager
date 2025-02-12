"""
You must write your views here, views are just some functions
"""

import logging
from decimal import Decimal as d

import trade.funcs as funcs
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import serializers
from django.db.models import QuerySet

# from django.contrib.auth import login
# from django.contrib.auth import authenticate
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import render  # returns a HttpResponse
from django.shortcuts import get_object_or_404, redirect

# from django.http import HttpResponse
from django.urls import reverse  # creates urls from url names
from django.utils.translation import gettext as _  # translation
from icecream import ic
from trade.models import Broker, RR_Stop_Factory, Symbol, Trade, UserBroker

logger = logging.getLogger("django")


def index(req):
    """_summary_

    Args:
        req (_type_): _description_

    Returns:
        _type_: _description_
    """
    return render(req, "trade/index.html", locals())


@login_required()
def new(req):
    """it's the view that shows the new trade form.

    Args:
        req (_type_): _description_
    """
    # if we came from new_commit() view
    # logger.warn("[trade.new: View]")
    viewname = "new"
    msg = None
    for m in get_messages(req):
        msg = m
        break
    commited = _("Saved") if msg is not None else _("Not Saved Yet")
    title = _("New Trade")

    broker = Broker.objects.all()
    return render(req, "trade/new.html", locals())


@login_required()
def new_commit(req):
    """Here we *received* from data from 'new' view. we save the data into db here and the
    will go back to 'new' view.

    Args:
        req (_type_): _description_
    """
    viewname = "new"
    p = funcs.Post(req)  # validate and get the posted data
    # Let's get our models and create a new instance
    broker: Broker = None
    symbol: Symbol = None
    user: User = None
    commission: d | None = None

    if req.user.is_authenticated:
        # a new instance of user
        user = User.objects.get(username=req.user)
    else:
        # We should go to log-in page
        redirect("accounts/login")

    # find the broker and put it inside a new instance
    broker, created = Broker.objects.get_or_create(name=p.get("broker"))

    # determine the commission
    if p.get("commission") is not None and p.get("commission") != "":
        commission = d(p.get("commission"))
    else:
        commission = d(broker.defaultCommission)

    symbol, created = Symbol.objects.get_or_create(
        name=p.get("symbol"), broker=broker, commission=commission
    )

    # First we need to get the last user broker to set the balance and reserve
    # of them
    ub_last = UserBroker.objects.last()
    # Then we need to create the new row for user broker for our new trade
    # (WHY?) because we can have a history and can correct our mistakes laters
    ub = UserBroker.objects.create(
        user=user,
        broker=broker,
        balance=ub_last.balance,
        reserve=ub_last.reserve,
        reservePercent=ub_last.reservePercent,
        riskPercent=ub_last.riskPercent,
    )
    # We don't know user sent us (stop_loss_percentage, risk_reward) or (entry, stop, target)
    # So we are using a *factory* that decide which **strategy** based on user inputs should be used
    # for computing risk_reward and stop_loss_percentage
    factory = RR_Stop_Factory().create(
        entry=d(p.get("entry", None)),
        stop=d(p.get("stop", None)),
        target=d(p.get("target", None)),
        risk_reward=d(p.get("risk_reward", None)),
        stop_loss_percentage=d(p.get("stop_loss_percentage", None)),
        result=None,
    )
    # Relationship, and we know that already there exists a user and a symbol
    # we already created
    Trade.objects.create(
        ub=ub,
        symbol=symbol,
        entry=d(p.get("entry", 0.0)),
        stop=d(p.get("stop", 0.0)),
        target=d(p.get("target", 0.0)),
        risk_reward=factory.get_risk_reward(),
        stop_percent=factory.get_stop_percentage(),
        amount=d(p.get("amount", 0.0)),
        picture=p.get("picture"),
        comment=p.get("comment"),
        timeFrame=p.get("timeframe"),
        strategy=p.get("strategy"),
    )
    url = reverse(
        "new_trade",
        kwargs={},
    )
    messages.info(
        req, "success"
    )  # send a message to front-end to notify it that data is saved
    return HttpResponsePermanentRedirect(url)

    # # fill the Relationship of UserBroker with broker and user
    # try:
    #     user_broker = UserBroker.objects.get(
    #         broker=broker,
    #         user=user
    #     )
    # except UserBroker.DoesNotExist:
    #     user_broker = None

    # TODO
    # user_broker.balance =
    # user_broker.riskPercent =
    # user_broker.reserve =

    # TODO
    # us.result = p.get('result')
    # TODO
    # us.isPositionChanged = bool(p.get(''))


@login_required()
def balance(req):
    """
    If User wanted to add +money or withraw -money from
    his/her balance
    """
    viewname = "balance"
    # if we came from new_commit() view
    # logger.warn("[trade.new: View]")
    msg = None
    for m in get_messages(req):
        msg = m
        break
    title = _("Add/Remove Balance")
    user: User = None
    if req.user.is_authenticated:
        user = User.objects.get(username=req.user)

    # NOTE: Use below codes if you want only add/remove balance to the brokers you already traded:
    ubs: QuerySet[UserBroker] = UserBroker.objects.select_related("broker").filter(
        user=user
    )
    # q = ubs.query # this will show the actuall SQL Query as a string
    # data_json = serializers.serialize("json", ubs)
    brokers_of_user: dict = {}
    list_of_brokers_of_user: list = []
    for ub in ubs:
        brokers_of_user[ub.broker.name] = ub
    mylist = list(brokers_of_user.values())
    for ub in mylist:
        list_of_brokers_of_user.append(
            {"name": ub.broker.name, "balance": ub.balance, "reserve": ub.reserve}
        )

    brokers = Broker.objects.all()
    return render(req, "trade/add_balance.html", locals())


@login_required()
def balance_commit(req):
    p = funcs.Post(req)  # validate and get the posted data
    if req.user.is_authenticated:
        user: User = User.objects.get(username=req.user)  # type: ignore
    broker = p.get("broker")
    balance: d = d(p.get("balance"))  # type: ignore
    broker_object = Broker.objects.get(name=broker)

    try:
        last_user_balance_in_this_broker = d(
            UserBroker.objects.filter(user=user, broker=broker_object).last().balance
        )
        if last_user_balance_in_this_broker + balance >= d(0):
            UserBroker.objects.create(
                broker=broker_object,
                user=user,
                balance=last_user_balance_in_this_broker + balance,
            )
            messages.info(req, "success")
    except:
        if balance >= d(0):
            UserBroker.objects.create(
                broker=broker_object,
                user=user,
                balance=balance,
            )
            messages.info(req, "success")

    return HttpResponsePermanentRedirect(
        reverse(
            "addremove_balance",
            kwargs={},
        )
    )


def api_commission(req):
    if req.method == "GET":
        symbol_name = req.GET.get("symbol")
        broker_name = req.GET.get("broker")

        broker: Broker = Broker.objects.get(name=broker_name)
        symbol: Symbol = get_object_or_404(Symbol, name=symbol_name, broker=broker)
        # symbol: Symbol = Symbol.objects.get(name=symbol_name, broker=broker)

        commission = None
        # us: UserSymbol = UserSymbol.objects.filter(user=user, symbol=symbol).first()
        if symbol.commission != broker.defaultCommission:
            commission = symbol.commission
        else:
            commission = broker.defaultCommission

        # ic(commission)
        return JsonResponse(commission, safe=False)


def api_risk(req):
    if req.method == "GET":
        user = None
        if req.user.is_authenticated:
            user = User.objects.get(username=req.user)

        broker_name = req.GET.get("broker")
        sym_name = req.GET.get("symbol")
        broker: Broker = Broker.objects.get(name=broker_name)
        ub: UserBroker = UserBroker.objects.filter(user=user, broker=broker).last()
        sym: Symbol = Symbol.objects.filter(broker=broker, name=sym_name).first()
        if sym:
            trade: Trade = (
                Trade.objects.filter(ub=ub, symbol=sym).order_by("-id").first()
            )
        if trade:
            # ic(trade.risk)
            return JsonResponse(trade.risk, safe=False)
        else:
            return JsonResponse({"message": "No trades found"}, status=404, safe=False)
