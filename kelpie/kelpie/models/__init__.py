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
    implements(IModel)
    __tablename__ = 'servers'
    id = Column(Integer, primary_key = True)
    name = Column(String(100), unique=True)
    ssh_url = Column(String(100))
    ssh_user = Column(String(25))
    zope_instances = relation('ZopeInstance', backref='server')

    def __repr__(self):
        return self.name

crud.register(Server,
    pretty_name = 'Server',
    slug_fn = lambda a: a.id,
    title_fn = lambda a: a.name,
    subitems = {
        'zopes' : Section(ZopeInstance, 'Zope instances')
    }
    )
    
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

crud.register(ZopeInstance,
    pretty_name = 'Zope Instance',
    slug_fn = lambda a: a.id,
    title_fn = lambda a: a.name,
    subitems = {
        'products' : Section(Product, 'Product')
    }
    )


class BuildoutInstance(Base):
    __tablename__ = 'buildout_instances'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    zope_instance_id = Column(Integer, ForeignKey('zope_instances.id'))
    filesystem_path = Column(String(255))
    project_id = Column(Integer, ForeignKey('projects.id'))

    def __repr__(self):
        return self.name

crud.register(BuildoutInstance,
    pretty_name = 'Buildouts',
    slug_fn = lambda a: a.id,
    title_fn = lambda a: a.name,
    subitems = {
        'products' : Section(Product, 'Product')
    }
    )

    
class ZopeProduct(Base):
    __tablename__ = 'zope_products'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    version = Column(String(20))
    zope_instance_id = Column(Integer, ForeignKey('zope_instances.id')) 

    def __repr__(self):
        return "%s (%s)" % (self.name, self.version)

crud.register(ZopeProduct,
    pretty_name = 'Product',
    slug_fn = lambda a: a.id,
    title_fn = lambda a: a.name,
    )

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key = True)
    name = Column(String(100))
    vcs_url = Column(String(255))
    buildout_instances = relation('BuildoutInstance', backref='project')

    def __repr__(self):
        return self.name

crud.register(Project,
    slug_fn = lambda a: a.id,
    title_fn = lambda a: a.name,
    )

root = crud.ApplicationRoot(
    subsections = {
        'zopes' : crud.Section(ZopeInstance, "Zope Instances"),
        'servers' : crud.Section(Server, "Servers"),
    }
)

crud.crud_init(DBSession, root)
    
def initialize_sql(db, echo=False):
    engine = create_engine(db, echo=echo)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    
    from crud import crud_init
    crud_init(DBSession)
    try:
        session = DBSession()
        instance = ZopeInstance()
        instance.name = 'A zope instance'
        instance.url = 'http://localhost:8080/'
        session.add(instance)
        transaction.commit()
    except IntegrityError:
        # already created
        pass


