import schemaish
import formish

from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.properties import SynonymProperty
from sqlalchemy.orm import compile_mappers, object_session, class_mapper
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.scoping import ScopedSession
from sqlalchemy.orm.dynamic import DynamicAttributeImpl
from sqlalchemy.util import OrderedDict

from sqlalchemy.orm.attributes import manager_of_class

from sqlalchemy.orm.attributes import ScalarAttributeImpl, ScalarObjectAttributeImpl, CollectionAttributeImpl, InstrumentedAttribute

from sqlalchemy import types as sa_types

def _get_attribute(cls, p):
    manager = manager_of_class(cls)
    return manager[p.key]

SA_TO_SCHEMAISH_MAPPING = {
    sa_types.String:    schemaish.String,
    sa_types.Integer:   schemaish.Integer,
}

class FormishSAReflector:
    """
    Reflects an SQLAlchemy model to a Formish schema
    """
    schema = schemaish.Structure()
    schema.add('title', schemaish.String())

    def __init__(self):
        self._fields = OrderedDict()
        self._render_fields = OrderedDict()
        self.model = self.session = None

    def sa_to_schemaish_type(self, field_type):
        return SA_TO_SCHEMAISH_MAPPING.get(field_type.__class__, None)
        
        
    def reflect(self, model):
    
        if not model:
            raise Exception('model parameter may not be None')

        cls = isinstance(model, type) and model or type(model)
        try:
            class_mapper(cls)
        except:
            raise Exception("Class not bound to a SA instance")

        schema = schemaish.Structure()

        # SA class.
        # load synonyms so we can ignore them
        synonyms = set(p for p in class_mapper(cls).iterate_properties 
                       if isinstance(p, SynonymProperty))
        # attributes we're interested in
        attrs = []
        for p in class_mapper(cls).iterate_properties:
            attr = _get_attribute(cls, p)
            if ((isinstance(p, SynonymProperty) or attr.property.key not in (s.name for s in synonyms))
                and not isinstance(attr.impl, DynamicAttributeImpl)):
                attrs.append(attr)
                print "Got field: %s" % attr.property.key
                
                impl = attr.impl
                print "impl is %s" % impl
                
                is_scalar_relation = isinstance(impl, ScalarObjectAttributeImpl)
                is_collection = isinstance(impl, CollectionAttributeImpl)
                print "-- is_scalar_relation: %s" % is_scalar_relation
                print "-- is_collection: %s" % is_collection
                
                print attr.property.__dict__.keys()
                
                if hasattr(attr.property, 'columns'):
                    print "TYPE IS %s" % attr.property.columns[0].type
                    sc_field = self.sa_to_schemaish_type(attr.property.columns[0].type)
                    schema.add(attr.property.key, sc_field)
                                      
        # sort relations last before storing in the OrderedDict
        #L = [fields.AttributeField(attr, self) for attr in attrs]
        #L.sort(lambda a, b: cmp(a.is_relation, b.is_relation)) # note, key= not used for 2.3 support
        #self._fields.update((field.key, field) for field in L)

        form = formish.Form(schema, "test-form")       
        return form

