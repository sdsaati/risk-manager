"""
You must write your views here, views are just some functions
"""
from django.shortcuts import render  # returns a HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponse
from django.urls import reverse  # creates urls from url names
from django.utils.translation import gettext as _  # translation
from trade.models import UserBroker, Broker, Symbol, UserSymbol
import trade.funcs as funcs
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from django.contrib.auth import login
# from django.contrib.auth import authenticate


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
    broker = Broker()
    symbol = Symbol()
    user = None
    user_broker = UserBroker()
    us = UserSymbol()

    if req.user.is_authenticated:
        user = User(username=req.user)
        us.user = user
    else:
        # We should go to log-in page
        redirect('accounts/login')

    symbol.name = p.get('symbol')
    broker.name = p.get('broker')
    user_broker.broker = broker
    # user_broker.balance =
    user_broker.user = user
    # user_broker.riskPercent =
    # user_broker.reserve =
    us.symbol = symbol
    us.entry = p.get('entry')
    us.target = p.get('target')
    us.stop = p.get('stop')
    # us.date =
    # us.result = p.get('result')
    us.amount = p.get('amount')
    us.riskReward = p.get('riskReward')
    us.commission = p.get('commission')
    us.picture = p.get('picture')
    us.comment = p.get('comment')
    us.isPositionChanged = p.get('')
    us.timeFrame = p.get('timeframe')
    us.strategy = p.get('strategy')

    # trades = UserSymbol.objects.get(id='')
    url = reverse('new_trade', kwargs={}, )
    messages.info(req, "success")
    return HttpResponsePermanentRedirect(url)
    return HttpResponse()
