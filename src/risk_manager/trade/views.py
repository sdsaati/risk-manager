"""
You must write your views here, views are just some functions
"""
from icecream import ic
from django.shortcuts import render  # returns a HttpResponse
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect
# from django.http import HttpResponse
from django.urls import reverse  # creates urls from url names
from django.utils.translation import gettext as _  # translation
from trade.models import UserBroker, Broker, Symbol, Trade
import trade.funcs as funcs
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from django.contrib.auth import login
# from django.contrib.auth import authenticate
from django.http import JsonResponse


def index(req):
    """_summary_

    Args:
        req (_type_): _description_

    Returns:
        _type_: _description_
    """
    return render(req, 'trade/index.html', locals())


@login_required()
def new(req):
    """ it's the view that shows the new trade form.

    Args:
        req (_type_): _description_
    """
    # if we came from new_commit() view
    msg = None
    for m in get_messages(req):
        msg = m
        break
    commited = _('Saved') if msg is not None else _('Not Saved Yet')
    title = _('New Trade')

    broker = Broker.objects.all()
    return render(req, 'trade/new.html', locals())


@login_required()
def new_commit(req):
    """ we come here from 'new' view. we save the data into db here and the
    will go back to 'new' view.

    Args:
        req (_type_): _description_
    """
    p = funcs.Post(req)  # validate and get the posted data
    # Let's get our models and create a new instance
    broker: Broker = None
    symbol: Symbol = None
    user: User = None
    commission: float = None

    if req.user.is_authenticated:
        # a new instance of user
        user = User.objects.get(username=req.user)
    else:
        # We should go to log-in page
        redirect('accounts/login')

    # find the broker and put it inside a new instance
    broker, created = Broker.objects.get_or_create(name=p.get('broker'))

    # determine the commission
    if p.get('commission') is not None and p.get('commission') != '':
        commission = float(p.get('commission'))
    else:
        commission = float(broker.defaultCommission)

    symbol, created = Symbol.objects.get_or_create(name=p.get('symbol'),
                                                   broker=broker,
                                                   commission=commission)

    # Relationship, and we know that already there exists a user and a symbol
    # we already created
    Trade.objects.create(
        user=user,
        symbol=symbol,
        entry=float(p.get('entry', 0.0)),
        stop=float(p.get('stop', 0.0)),
        target=float(p.get('target', 0.0)),
        amount=float(p.get('amount', 0.0)),
        riskReward=float(p.get('riskReward', 2)),
        picture=p.get('picture'),
        comment=p.get('comment'),
        timeFrame=p.get('timeframe'),
        strategy=p.get('strategy'),
    )
    url = reverse(
        'new_trade',
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


def api_commission(req):
    if req.method == "GET":
        symbol_name = req.GET.get("symbol")
        broker_name = req.GET.get("broker")

        broker: Broker = Broker.objects.get(name=broker_name)
        symbol: Symbol = get_object_or_404(Symbol,
                                           name=symbol_name,
                                           broker=broker)
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
        ub: UserBroker = UserBroker.objects.get(user=user, broker=broker)
        sym: Symbol = Symbol.objects.filter(broker=broker,
                                            name=sym_name).first()
        if sym:
            trade: Trade = Trade.objects.filter(
                ub=ub, symbol=sym).order_by('-id').first()
        if trade:
            # ic(trade.risk)
            return JsonResponse(trade.risk, safe=False)
        else:
            return JsonResponse({"message": "No trades found"},
                                status=404,
                                safe=False)
