import transaction

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relation, backref

from sqlalchemy.ext.declarative import declarative_base

from zope.interface import implements

from zope.sqlalchemy import ZopeTransactionExtension

import crud
from crud.forms.fa import FormAlchemyFormFactory

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

# Set the form factory for allinstances of ModelProxy
crud.ModelProxy.form_factory = FormAlchemyFormFactory()

class Server(Base):
    __tablename__ = 'servers'
    id = Column(Integer, primary_key = True)
    name = Column(String(100), unique=True)
    ssh_url = Column(String(100))
    ssh_user = Column(String(25))
    zope_instances = relation('ZopeInstance', backref='server')

    def __repr__(self):
        return self.name
    
class ZopeInstance(Base):
    """ The SQLAlchemy declarative model class for a Page object. """
    __tablename__ = 'zope_instances'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    url = Column(String(255))
    server_id = Column(Integer, ForeignKey('servers.id'))
    buildout_instances = relation('BuildoutInstance', backref='zope_instance')
    products = relation('ZopeProduct', backref='zope_instance')

    def __repr__(self):
        return self.name


class BuildoutInstance(Base):
    __tablename__ = 'buildout_instances'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    zope_instance_id = Column(Integer, ForeignKey('zope_instances.id'))
    filesystem_path = Column(String(255))
    project_id = Column(Integer, ForeignKey('projects.id'))

    def __repr__(self):
        return self.name

    
class ZopeProduct(Base):
    __tablename__ = 'zope_products'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    version = Column(String(20))
    zope_instance_id = Column(Integer, ForeignKey('zope_instances.id')) 

    def __repr__(self):
        return "%s (%s)" % (self.name, self.version)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key = True)
    name = Column(String(100))
    vcs_url = Column(String(255))
    buildout_instances = relation('BuildoutInstance', backref='project')

    def __repr__(self):
        return self.name

# Self-referential test

class Folder(Base):
    __tablename__ = 'folders'
    id = Column(Integer, primary_key = True)
    name = Column(String(100))
    parent_id = Column(Integer, ForeignKey('folders.id')) 
    subfolders = relation('Folder')#, backref=backref('parent', remote_side=['folders.c.id']))

    def __repr__(self):
        return self.name

# Register our classes with crud
class ServerProxy(crud.ModelProxy):
    pretty_name = 'Server'
    subsections = {
        'zopes' : crud.Section('Zope Instances', 'zope_instances'),
    }

crud.register(Server, ServerProxy)

class ZopeInstanceProxy(crud.ModelProxy):
    pretty_name = 'Zope Instance',

    subsections = {
        'products' : crud.Section('Products', 'products'),
        'buildouts' : crud.Section('Buildouts', 'buildout_instances'),
    }
    
    edit_form_options = {}

crud.register(ZopeInstance, ZopeInstanceProxy)

crud.register(BuildoutInstance)
crud.register(ZopeProduct)
crud.register(Project)

about_section = crud.Section(
    "About", 
    subsections = {
   'one' : crud.Section('Page One!'),
   'two' : crud.Section('A folder!',
        subsections = {
            'uno' : crud.Section("Uno!"),
            'duo' : crud.Section("Duo!"),
        })
    }
)

about_section.show_in_breadcrumbs = False

class FolderProxy(crud.ModelProxy):
    pretty_name = 'Folder',
    subitems_source = 'subfolders'

class RootFolderProxy(crud.ModelProxy):


    subitems_source = 'subfolders'

    def __init__(self):
        self.__name__ = None
        self.__parent__ = None
        
    @property
    def model(self):
        return DBSession.query(Folder).filter(Folder.id==1).first()
        
    def with_parent(self, parent, name):
        self.__name__ = name
        self.__parent__ = parent
        return self
    
        
crud.register(Folder, FolderProxy)



root = crud.Section(
    "Kelpie!",
    subsections = dict(
        zopes = crud.Section("All Zope Instances", ZopeInstance),
        servers = crud.Section("All Servers", Server),
        products = crud.Section("All Products", ZopeProduct),
        about = about_section, 
        folders = RootFolderProxy(),
        )
)

#from crud.forms import FormishSAReflector
#reflector = FormishSAReflector()
#form = reflector.reflect(ZopeInstance)
#print "Got form: %s" % (form())
    
def initialize_sql(db, echo=False):
    engine = create_engine(db, echo=echo)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)    
    #root = RootFolderProxy()
    print "GOT ROOT: %s" % root
    crud.crud_init(DBSession, root)


