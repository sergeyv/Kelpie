from crud.registry import get_typeinfo_by_slug
from zope.interface import Interface
from zope.interface import implements

from repoze.bfg.url import model_url

from sqlalchemy import orm

DBSession = None

class IModel(Interface):
    """ """
class ISection(Interface):
    """ """
           
        
class ApplicationRoot(object):

    def __init__(self, subsections):
        self.__name__ = ''
        self.__parent__ = None
        self.subsections = subsections

    def __getitem__(self, name):
        #s = Section()
        #s.typeinfo = get_typeinfo_by_slug(name)
        s = self.subsections[name]
        s.__parent__ = self
        s.__name__ = name
        return s

section_views = ('add','save','delete')

class Section(object):
    implements(ISection)

    def __init__(self, class_, title):
        self.class_ = class_
        self.title = title

    def __getitem__(self, name):
        if name in section_views:
            raise KeyError
        try:
            obj = DBSession.query(self.class_).filter(self.class_.id==name).one()
        except orm.exc.NoResultFound:
            raise KeyError
            
        print "Found %s" % obj
        obj.__parent__ = self
        obj.__name__ = name
        print "obj.__name__ = %s" % obj.__name__
        return obj
        
    def section_url(self, request, *args):
        str_args = []
        for arg in args:
            if IModel.providedBy(arg):
                ### TODO: Do some fancy sluggification here
                arg = str(arg.id)
            else:
                arg = str(arg)
            str_args.append(arg)
                
        return model_url(self, request, *str_args)

        
crud_root = None

def get_root(environ=None):
    return crud_root
    
def crud_init( session, root ):
    global DBSession
    DBSession = session
    
    global crud_root
    crud_root = root


