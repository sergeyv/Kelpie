
content_types_registry = dict()

def register(cls, slug):
    content_types_registry[slug] = { 
        'class' : cls,
    }

def get_content_type(slug):
    return content_types_registry[slug]
