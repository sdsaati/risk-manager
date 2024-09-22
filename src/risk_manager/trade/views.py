"""
You must write your views here, views are just some functions
"""
from django.shortcuts import render  # returns a HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse  # creates urls from url names
from django.utils.translation import gettext as _  # translation
from trade.models import User, UserBroker, Broker, Symbol, UserSymbol


def index(req):
    """_summary_

    Args:
        req (_type_): _description_

    Returns:
        _type_: _description_
    """
    return render(req, 'trade/index.html', locals())


def new(req, status='none'):
    """_summary_

    Args:
        req (_type_): _description_
    """
    # if we came from new_commit() view
    commited = 'Saved' if status != 'none' else 'Not Saved Yet'
    title = _('New Trade')

    return render(req, 'trade/new.html', locals())


def new_commit(req):
    """_summary_

    Args:
        req (_type_): _description_
    """
    # check for data:
    if req.method == 'POST':
        req.POST.
    # trades = UserSymbol.objects.get(id='')
    url = reverse('new_trade_with_status', kwargs={'status': 'success'}, )
    return HttpResponsePermanentRedirect(url)
