import sys
if sys.version_info[0] < 3:
    from collections import Mapping
else:
    from collections.abc import Mapping
from utils.properties import weak, roproperty
from ..generic import MemoryBase
from .action import MemoryTypeActionSketch


@weak("_owner")
class MemoryTypeActions(MemoryBase, Mapping):

    def __init__(self, owner):
        self._owner = owner
        self._items = {}
        self._items_by_scope = {}

    owner = roproperty("_owner")

    def on_complete(self, item):
        self._items[item.scope, item.name] = item
        if item.scope in self._items_by_scope:
            items = self._items_by_scope[item.scope]
        else:
            self._items_by_scope[item.scope] = items = {}
        items[item.scope, item.name] = item

    def new_sketch(self, restore=False):
        return MemoryTypeActionSketch(self)

    # unsafe
    def compose(self, ident=u"", file=None):
        if self._items:
            file.write(u"%s<Actions>\n" % ident)
            for scope, scope_actions in self._items_by_scope.items():
                file.write(u"%s\t<Container ID=\"%s\">\n" % (ident, scope))
                for action in scope_actions.values():
                    action.compose(ident=ident + u"\t\t", file=file)
                file.write(u"%s\t</Container>\n" % ident)
            file.write(u"%s</Actions>\n" % ident)

    def __getitem__(self, key):
        try:
            return self._items[key]
        except KeyError:
            return iter(self._items_by_scope[key].values())

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "actions of %s" % self._owner
