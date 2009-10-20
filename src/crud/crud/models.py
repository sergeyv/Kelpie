from zope.interface import Interface
from zope.interface import implements

from repoze.bfg.url import model_url

from sqlalchemy import orm

DBSession = None

class IModel(Interface):
    """ """
class ISection(Interface):
    """ """
class ModelProxy(object):
    implements(IModel)
    def __init__(self, name, parent, model):
        self.__name__ = name
        self.__parent__ = parent
        self.model = model   

    def __repr__(self):
        return self.model.__repr__()       
        
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


class SectionFactory(object):
    def __init__(self, title, relation_name, name=None):
        self.title = title
        self.relation_name = relation_name
        self.name = name or relation_name
    
    def create_section(self, parent):
        section = Section(self.title, self.relation_name)
        section.__parent__ = parent
        section.__name__ = self.name

        
class Section(object):
    implements(ISection)

    def __init__(self, title, relation_name):
        self.title = title
        self.relation_name = relation_name

    def __getitem__(self, name):
        if name in section_views:
            raise KeyError
        try:
            query = DBSession.query(self.class_).filter(self.class_.id==name)
            if self.join_field:
                query = query.filter(self.join_field == __parent__.id)
            obj = query.one()
        except orm.exc.NoResultFound:
            raise KeyError
            
        print "Found %s" % obj
        #obj.__parent__ = self
        #obj.__name__ = name
        print "obj.__name__ = %s" % obj.__name__
        return ModelProxy(self, name, model)
        
    def section_url(self, request, *args):
        # args contain ModelProxies, not real objects
        str_args = []
        for arg in args:
            if IModel.providedBy(arg):
                ### TODO: Do some fancy sluggification here
                arg = str(arg.model.id)
            else:
                arg = str(arg)
            str_args.append(arg)
                
        return model_url(self, request, *str_args)

class RootSection(object):
    implements(ISection)

    def __init__(self, class_, title):
        self.class_ = class_
        self.title = title

    def __getitem__(self, name):
        if name in section_views:
            raise KeyError
        try:
            query = DBSession.query(self.class_).filter(self.class_.id==name)
            obj = query.one()
        except orm.exc.NoResultFound:
            raise KeyError           
        return ModelProxy(self, name, obj)
        
    def section_url(self, request, *args):
        str_args = []
        for arg in args:
            if IModel.providedBy(arg):
                ### TODO: Do some fancy sluggification here
                arg = str(arg.model.id)
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


