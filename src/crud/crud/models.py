from zope.interface import Interface
from zope.interface import implements

from webob.exc import HTTPNotFound
from repoze.bfg.url import model_url
from repoze.bfg.traversal import find_interface

from sqlalchemy import orm

from crud.registry import get_proxy_for_model

DBSession = None

class IModel(Interface):
    """ """
class ISection(Interface):
    """ """

def get_related_by_id(obj, id, property_name=None):
    relation = getattr(obj.__class__, property_name)
    related_class = relation.property.argument()
    print "related class is %s" % related_class
    q = DBSession.query(related_class)
    q = q.with_parent(obj, property_name)
    q = q.filter_by(id=int(id))
    result = q.first() 
    return result

class Traversable(object):
    """
    A base class which implements stuff needed
    for 'traversability'
    """
    __name__ = ''
    __parent__ = None
    subsections = {}
    subitems_source = None
    views = []

    def url(self, request, view_method=None):
        print "getting url for %s" % self
        print "    parent is %s" % self.__parent__
        print "    name is %s" % self.__name__
        print "    url is %s" % model_url(self, request)
        if view_method:
            return model_url(self, request, view_method)
        else:
            return model_url(self, request)

    def parent_url(self, request):
        return model_url(self.__parent__, request)

    def __getitem__(self, name):
    
        # 1. check if it's our own view
        ## TODO: Try to get a real view using queryMultiAdapter here
        ## get rid of self.views
        if name in self.views:
            raise KeyError

        # 2. check if it's our subsection
        s = self.subsections.get(name, None)
        if s is not None:
            return s.with_parent(self, name)
            
        # 3. look up subitems
        if isinstance(self.subitems_source, str):
            model = get_related_by_id(self.__parent__.model, name, self.subitems_source)
        else:
            model = DBSession.query(self.subitems_source)\
                .filter(self.subitems_source.id==name).first()
        if model is None:
            raise KeyError       
        proxy_class = get_proxy_for_model(model.__class__)
        print "Proxy for %s is %s" % (model.__class__, proxy_class) 
        return proxy_class(name=name, parent=self, model=model)

    def get_subsections(self):
        return [s.with_parent(self,n) for (n,s) in self.subsections.items()]

    def parent_model(self):
        model = find_interface(self, IModel)
        return model
        
    def parent_section(self):
        section = find_interface(self, ISection)
        return section
        
    def get_subitems_class(self):    
        if isinstance(self.subitems_source, str):
            parent_model = self.parent_model()
            relation = getattr(parent_model.model.__class__, self.subitems_source)
            related_class = relation.property.argument()
            return related_class
        else:
            return self.subitems_source

    def get_items(self):
        if self.subitems_source is None:
            return []
        if isinstance(self.subitems_source, str):
            related_class = self.get_subitems_class()
            parent_class = self.__parent__.model
            print "related class is %s" % related_class
            q = DBSession.query(related_class)
            q = q.with_parent(parent_class, self.subitems_source)
        else:
            q = DBSession.query(self.subitems_source)
        result = q.all() 
        # wrap them in the location-aware proxy
        result = [ModelProxy(name=str(obj.id), parent=self, model=obj) for obj in result]
        return result
    
    
class ModelProxy(Traversable):
    implements(IModel)

    pretty_name = 'Model'

    views = ('edit', 'save', 'delete')
    
    def __init__(self, name, parent, model):
        self.__name__ = name
        self.__parent__ = parent
        self.model = model   

    def __repr__(self):
        return self.model.__repr__()       
        
    @property
    def title(self):
        return getattr(self.model, 'title',
                    getattr(self.model, 'name',
                    "%s %s" % (self.pretty_name, self.model.id)))
        
class Section(Traversable):
    implements(ISection)

    views = ('add','save','delete')

    def __init__(self, title, subitems_source=None, subsections = {}):
        self.title = title
        self.subitems_source = subitems_source
        self.subsections = subsections
        
    def __repr__(self):
        return "Section %s (%s)" % (self.title, self.subitems_source)

    def with_parent(self, parent, name):
        """
        returns a copy of the section 
        inserted in the 'traversal context'
        """
        #if self.__parent__ == parent:
        #    self.__name__ = name
        #    return self
        section = self.__class__(title=self.title,
            subitems_source=self.subitems_source,
            subsections = self.subsections )
        section.__name__ = name
        section.__parent__ = parent
        return section
                
        
    def child_url(self, request, *args):
        # args contain ModelProxies, not real objects
        str_args = []
        for arg in args:
            print arg
            if IModel.providedBy(arg):
                ### TODO: Do some fancy sluggification here
                arg = str(arg.model.id)
            else:
                arg = str(arg)
            str_args.append(arg)
                
        print "self: %s, request:%s, args: %s, str_args: %s" % (self, request, args, str_args)
        return model_url(self, request, *str_args)
        

        
crud_root = None

def get_root(environ=None):
    return crud_root
    
def crud_init( session, root ):
    global DBSession
    DBSession = session
    
    global crud_root
    crud_root = root


