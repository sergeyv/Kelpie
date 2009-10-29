from zope.interface import Interface
from zope.interface import implements

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
        #s = Section()
        #s.typeinfo = get_typeinfo_by_slug(name)
        s = self.subsections[name]
        s.__parent__ = self
        s.__name__ = name
        return s

from sqlalchemy.orm import compile_mappers, class_mapper
from sqlalchemy.orm.properties import RelationProperty

class SectionFactory(object):
    def __init__(self, relation_prop, title, name=None):
        self.title = title
        self.relation = relation_prop
        #TODO: get section's class name here using our parent class and relation name
        #(through mappers I guess
        self.name = name or self.relation.key
        #mapper = class_mapper(parent_class)
        #prop = getattr(mapper, relation_name, None)
        print "*"*80
        for (name, value) in relation_prop.__dict__.items():
            print "%s: %s" % (name, value)
        print "-"*80
        p = relation_prop.parententity.get_property(relation_prop.key)
        print p.__class__
        for (name, value) in p.__dict__.items():
            print "%s: %s" % (name, value)
        print "+"*80
        for (name, value) in p.__class__.__base__.__dict__.items():
            print "%s: %s" % (name, value)
    
    def create_section(self, parent):
        section = Section(self.title, self.relation_name)
        section.__parent__ = parent
        section.__name__ = self.name
        section.relation = self.relation
        return section

        
class Section(object):
    implements(ISection)

    def __init__(self, title, relation_name):
        self.title = title
        self.relation_name = relation_name

    def __getitem__(self, name):
        if name in section_views:
            raise KeyError
        try:
            #TODO: get just one object here using our relation property
            query = DBSession.query(self.class_).filter(self.class_.id==name)
            if self.join_field:
                query = query.filter(self.join_field == __parent__.id)
            obj = query.one()
        except orm.exc.NoResultFound:
            raise KeyError
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


