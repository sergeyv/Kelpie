
slug_registry = dict()
class_registry = dict()

def register(cls, **kwargs):
    ti = kwargs
    ti['class'] = cls
    slug = ti.get('slug', cls.__name__) 
    slug_registry[slug] = ti
    class_registry[cls] = ti

def get_typeinfo_by_slug(slug):
    return slug_registry[slug]

def get_typeinfo_by_class(cls):
    return class_registry[cls]

def get_registered_types():
    return slug_registry
