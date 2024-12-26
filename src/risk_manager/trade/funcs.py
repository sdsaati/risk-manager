from django.utils.translation import gettext as _  # translation
from trade.models import Trade
"""there are some usefull functions and classes here I wrote

    Returns:
        _type_: _description_
    """


class Post:
    """It's easier to use post"""

    def __init__(self, req):
        self.exists_post: bool = False
        self.req = req
        self.post = self.req.POST
        if self.req.method == "POST":
            self.exists_post = True

    def get(self, name: str, default=None):
        if self.exists_post and self.post.get(name) != "":
            return self.post.get(name)
        elif self.post.get(name) == "":
            return default
        else:
            return None

    def get_t(self, name: str, default=None):
        if self.exists_post and self.post.get(name) != "":
            return _(self.post.get(name))
        elif self.post.get(name) == "":
            return default
        else:
            return None
