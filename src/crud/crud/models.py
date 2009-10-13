from crud.registry import content_types_registry
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
        s.cls = content_types_registry[name]['class']
        return s

section_views = ('add','save','delete')

class Section(object):
    implements(ISection)
    def __getitem__(self, name):
        if name in section_views:
            raise KeyError
        return DBSession.query(self.cls).filter(self.cls.id==name).one()
        
        
crud_root = CrudRoot()

def get_root(environ):
    return crud_root
    