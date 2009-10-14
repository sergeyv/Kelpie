from crud.registry import get_typeinfo_by_slug
from zope.interface import Interface
from zope.interface import implements
DBSession = None

class IModel(Interface):
    """ """
class ISection(Interface):
    """ """
    
def crud_init(session):
    global DBSession
    DBSession = session
        
        
class CrudRoot(object):
    def __getitem__(self, name):
        s = Section()
        s.typeinfo = get_typeinfo_by_slug(name)
        return s

section_views = ('add','save','delete')

class Section(object):
    implements(ISection)
    def __getitem__(self, name):
        cls = self.typeinfo['class']
        if name in section_views:
            raise KeyError
        obj = DBSession.query(cls).filter(cls.id==name).one()
        return obj
        
        
crud_root = CrudRoot()

def get_root(environ):
    return crud_root
    
