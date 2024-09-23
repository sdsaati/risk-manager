from django.utils.translation import gettext as _  # translation
"""there are some usefull functions and classes here I wrote

    Returns:
        _type_: _description_
    """


class Post:
    """It's easier to use post
    """

    def __init__(self, req):
        self.exists_post: bool = False
        self.req = req
        self.post = self.req.POST
        if self.req.method == 'POST':
            self.exists_post = True

    def get(self, name: str):
        if self.exists_post:
            return self.post.get(name)

    def get_t(self, name: str):
        if self.exists_post:
            return _(self.post.get(name))
