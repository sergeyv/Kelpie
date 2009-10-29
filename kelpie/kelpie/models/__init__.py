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
from sqlalchemy.orm import relation

from sqlalchemy.ext.declarative import declarative_base

from zope.interface import implements

from zope.sqlalchemy import ZopeTransactionExtension

from crud import IModel

import crud

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


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

#from sqlalchemy.orm import compile_mappers, class_mapper
#from sqlalchemy.orm.properties import RelationProperty
#compile_mappers()

#mapper = class_mapper(ZopeInstance)

#for prop in mapper.iterate_properties:
#    print prop, prop.__class__
#    if prop.__class__ == RelationProperty:
#        print "TADA"
#        for (name, value) in prop.__dict__.items():
#            print "%s: %s" % (name, value)
    
# Register our classes with crud
class ServerProxy(crud.ModelProxy):
    pretty_name = 'Server'
    subsections = [
        crud.SectionFactory(Server.zope_instances, 'Zope instances', 'zope_instances'),
    ]

crud.register(Server, ServerProxy)

class ZopeInstanceProxy(crud.ModelProxy):
    pretty_name = 'Zope Instance',
    slug_fn = lambda a: a.id,
    title_fn = lambda a: a.name,
    subsections = [
        crud.SectionFactory(ZopeInstance.products, 'Products', 'products'),
        crud.SectionFactory(ZopeInstance.buildout_instances, 'Buildouts', 'buildout_instances'),
    ]

crud.register(ZopeInstance, ZopeInstanceProxy)

crud.register(BuildoutInstance)
crud.register(ZopeProduct)
crud.register(Project)

root = crud.ApplicationRoot(
    subsections = {
        'zopes' : crud.RootSection(ZopeInstance, "All Zope Instances"),
        'servers' : crud.RootSection(Server, "All Servers"),
        'products' : crud.RootSection(ZopeProduct, "All Products"),
    }
)

    
def initialize_sql(db, echo=False):
    engine = create_engine(db, echo=echo)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)    
    crud.crud_init(DBSession, root)


