from zope.interface import Interface
from zope.interface import implements

from webob.exc import HTTPNotFound
from repoze.bfg.url import model_url

from sqlalchemy import orm

from crud.registry import get_proxy_for_model

DBSession = None

class IModel(Interface):
    """ """
class ISection(Interface):
    """ """

section_views = ('add','save','delete')
model_views = ('edit', 'save', 'delete')

def get_related_by_id(obj, id, property_name=None):
    relation = getattr(obj.__class__, property_name)
    related_class = relation.property.argument()
    print "related class is %s" % related_class
    q = DBSession.query(related_class)
    q = q.with_parent(obj, property_name)
    q = q.filter_by(id=int(id))
    result = q.first() 
    return result

class ModelProxy(object):
    implements(IModel)

    pretty_name = 'Model'

    def __init__(self, name, parent, model):
        self.__name__ = name
        self.__parent__ = parent
        self.model = model   

    def __repr__(self):
        return self.model.__repr__()       

    def __getitem__(self, name):
        """ """
        if name in model_views:
            print "In model views"
            raise KeyError
        
        for factory in self.subsections:
            print "subsection %s, name is %s" % (factory.name, name)
            if factory.name == name:
                print "match!"
                return factory.create_section(self)
        print "No match"
        raise KeyError

        
class ApplicationRoot(object):

    def __init__(self, subsections):
        self.__name__ = ''
        self.__parent__ = None
        self.subsections = subsections

    def __getitem__(self, name):
        s = self.subsections[name]
        s.__parent__ = self
        s.__name__ = name
        return s

from sqlalchemy.orm import compile_mappers, class_mapper
from sqlalchemy.orm.properties import RelationProperty

class SectionFactory(object):
    def __init__(self, relation_name, title, name=None):
        self.relation_name = relation_name
        self.title = title
        self.name = name or self.relation_name
    
    def create_section(self, parent):
        section = Section(self.title, self.relation_name)
        section.__parent__ = parent
        section.__name__ = self.name
        section.relation_name = self.relation_name
        return section

        
class Section(object):
    implements(ISection)

    def __init__(self, title, relation_name):
        self.title = title
        self.relation_name = relation_name

    def __getitem__(self, name):
        if name in section_views:
            raise KeyError
        model = get_related_by_id(self.__parent__.model, name, self.relation_name)
        if model is None:
            raise HTTPNotFound       
        proxy_class = get_proxy_for_model(model.__class__)
        print "Proxy for %s is %s" % (model.__class__, proxy_class) 
        return proxy_class(self, name, model)
        
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
        
    def get_subitems_class(self):    
        relation = getattr(self.__parent__.model.__class__, self.relation_name)
        related_class = relation.property.argument()
        return related_class

    def get_items(self):
        # TODO: get all items which belong to our parent
        related_class = self.get_subitems_class()
        parent_class = self.__parent__.model
        print "related class is %s" % related_class
        q = DBSession.query(related_class)
        q = q.with_parent(parent_class, self.relation_name)
        #q = q.filter_by(id=int(id))
        result = q.all() 
        return result


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
            model = query.one()
        except orm.exc.NoResultFound:
            raise KeyError           
        proxy_class = get_proxy_for_model(model.__class__)
        print "Proxy for %s is %s" % (model.__class__, proxy_class) 
        return proxy_class(self, name, model)
        
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


