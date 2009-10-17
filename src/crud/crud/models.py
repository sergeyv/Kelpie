from crud.registry import get_typeinfo_by_slug
from zope.interface import Interface
from zope.interface import implements

DBSession = None

class IModel(Interface):
    """ """
class ISection(Interface):
    """ """
           
        
class ApplicationRoot(object):

    def __init__(self):
        self.__name__ = ''
        self.__parent__ = None
        self.subitems = {}

    def __getitem__(self, name):
        s = Section()
        s.typeinfo = get_typeinfo_by_slug(name)
        return s

section_views = ('add','save','delete')

class Section(object):
    implements(ISection)

    def __init__(self, class_, title):
        self.class_ = class_
        self.title = title

    def __getitem__(self, name):
        cls = self.typeinfo['class']
        if name in section_views:
            raise KeyError
        obj = DBSession.query(cls).filter(cls.id==name).one()
        return obj
        
        
crud_root = None

def get_root(environ):
    return crud_root
    
def crud_init(session,
    root,
    subsections ):
    global DBSession
    DBSession = session
    
    global crud_root
    crud_root = root


