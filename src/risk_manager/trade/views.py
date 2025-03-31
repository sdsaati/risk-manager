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


def get_user(req):
    """
    this is not a view, this is only a helper function that returns current user
    """
    if req.user.is_authenticated:
        return User.objects.get(username=req.user)
    else:
        redirect("accounts/login")


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

    user = get_user(req)

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
    broker: Broker = None  # type: ignore
    symbol: Symbol = None  # type: ignore
    commission: d | None = None  # type: ignore

    user = get_user(req)

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
    entry = p.get("entry", None)
    stop = p.get("stop", None)
    target = p.get("target", None)
    if entry is not None and stop is not None and target is not None:
        entry = d(entry)
        stop = d(stop)
        target = d(target)
    factory = RR_Stop_Factory().create(
        entry=entry,
        stop=stop,
        target=target,
        risk_reward=p.get("risk_reward", None),
        stop_percentage=p.get("stop_loss_percentage", None),
        result=None,
    )
    # Relationship, and we know that already there exists a user and a symbol
    # we already created
    Trade.objects.create(
        ub=ub,
        symbol=symbol,
        entry=entry,
        stop=stop,
        target=target,
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


@login_required()
def balance(req):
    """
    This is a form
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
    user = get_user(req)

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
    user = get_user(req)
    broker = p.get("broker")
    balance: d = d(p.get("balance"))  # type: ignore
    broker_object = Broker.objects.get(name=broker)

    try:
        last_user_balance_in_this_broker = d(
            UserBroker.objects.filter(
                user=user, broker=broker_object).last().balance
        )
        last_user_in_this_broker = UserBroker.objects.filter(
            user=user, broker=broker_object).last()
        if last_user_balance_in_this_broker + balance >= d(0):
            UserBroker.objects.create(
                broker=broker_object,
                user=user,
                balance=last_user_balance_in_this_broker + balance,
                reservePercent=last_user_in_this_broker.reservePercent,
                riskPercent=last_user_in_this_broker.riskPercent,
                reserve=last_user_in_this_broker.reservePercent *
                (last_user_balance_in_this_broker + balance) / d(100),
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


def api_all(req):
    if req.method == "GET":
        user: User = get_user(req)  # type: ignore
        broker_name = req.GET.get("broker")
        sym_name = req.GET.get("symbol")
        broker: Broker = Broker.objects.filter(
            name=broker_name).last()  # type: ignore
        ub: UserBroker = UserBroker.objects.filter(
            user=user, broker=broker).order_by("id").last()  # type: ignore
        sym: Symbol = Symbol.objects.filter(
            broker=broker, name=sym_name).order_by("id").last()  # type: ignore

        commission = None
        if sym.commission is None:
            commission = broker.defaultCommission
        else:
            commission = sym.commission

        return JsonResponse(
            {
                "balance": ub.balance,
                "defined_reserve": ub.defined_reserve,
                "risk_percent": ub.riskPercent,
                "reserve_percent": ub.reservePercent,
                "reserve": ub.reserve,
                "available": ub.available_balance,
                "risk": ub.risk,
                "commission": commission,
            },
            safe=False,
        )
