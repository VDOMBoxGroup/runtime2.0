
class Structure(object):

    def __init__(self, **keywords):
        self.__dict__.update(keywords)


VDOM_structure = Structure
