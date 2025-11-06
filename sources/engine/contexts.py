
from builtins import object
from utils.properties import roproperty


class EngineContext(object):

    def __init__(self, instance):
        self._instance = instance

    instance = roproperty("_instance")


class RenderContext(EngineContext):

    class RenderContextContentsLazyProperty(object):

        def __get__(self, instance, owner=None):
            instance._instance.execute()
            instance.contents = value = instance._instance.render()
            return value

    contents = RenderContextContentsLazyProperty()


class WysiwygContext(EngineContext):

    class WysiwygContextContentsLazyProperty(object):

        def __get__(self, instance, owner=None):
            instance.contents = value = instance._instance.wysiwyg()
            return value

    contents = WysiwygContextContentsLazyProperty()
