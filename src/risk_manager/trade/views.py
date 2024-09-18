"""
You must write your views here, views are just some functions
"""
from django.shortcuts import render  # returns a HttpResponse
from django.utils.translation import gettext as _  # translation


def index(req):
    """_summary_

    Args:
        req (_type_): _description_

    Returns:
        _type_: _description_
    """
    return render(req, 'trade/index.html', locals())


def new(req):
    """_summary_

    Args:
        req (_type_): _description_
    """
    title = _('New Trade')
    return render(req, 'trade/new.html', locals())
