
class_registry = list()

def register(cls, **kwargs):
    ti = kwargs
    ti['class'] = cls
    ti['slug_fn'] = ti.get('slug_fn', lambda a: a.id)
    ti['title_fn'] = ti.get('title_fn', lambda a: a.title)
    cls.crud_typeinfo = ti 
    class_registry.append(cls)

def get_registered_types():
    return class_registry
