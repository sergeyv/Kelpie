
from repoze.bfg.chameleon_zpt import render_template_to_response as render
from repoze.bfg import traversal

from webob.exc import HTTPFound
from formalchemy import FieldSet
from crud.models import DBSession

from crud import IModel, ISection, ModelProxy

from crud.views.theme import Theme

def index(context,request):
    # context is a Section object here
    theme = Theme(context, request)
    
    return render('templates/index.pt',
                  context=context,
                  request = request,
                  theme = theme,
                 )
                                       
def view(context, request):
    #context is ModelProxy here
    theme = Theme(context, request)

    fs = FieldSet(context.model)
    include = []
    # render context's fiels using FA
    # TODO: there's a way to set this on the form itself
    # rather than on individual fields
    for (k, field) in fs.render_fields.items():
        include.append(field.readonly())
    fs.configure(include=include)
    return render('templates/view.pt',
                   context = context,
                   form = fs.render(),
                   request = request,
                   theme = theme,
                  )

def edit(context, request):
    # context is ModelProxy here
    theme = Theme(context, request)
    #fs = FieldSet(context.model)
    import schemaish
    import formish
    schema = schemaish.Structure()
    schema.add('title', schemaish.String())
    form = formish.Form(schema, 'form')
    #form.addAction(save, 'Save')
    #form.addAction(add, 'Cancel')

    #form['title'].widget = formish.Input(strip=True)
    form['title'].default = "Hello!"
    return render('templates/edit.pt',
                  context = context,
                  theme=theme,
                  form = form(), #fs.render(),
                  request = request,
                 )

def add(context, request):
    # context is Section here
    theme = Theme(context, request)
    dbsession = DBSession()
    instance = context.create_subitem()
    fs = FieldSet(instance, session=dbsession)
    return render('templates/add.pt',
                  instance = instance,
                  theme = theme,
                  form = fs.render(),
                  context = context,
                  request = request,
                 )

def save(context, request):
    success_url = request.path_url.rpartition('/')[0]+ '/'
    failure_url = request.path_url.rpartition('/')[0] + '/edit'

    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
    instance = context.model
    dbsession = DBSession()
    fs = FieldSet(instance, session=dbsession)
    fs.rebind(instance, data=request.params)
    if fs.validate(): fs.sync()
    return HTTPFound(location=success_url)

def save_new(context, request):
    success_url = request.path_url.rpartition('/')[0]+ '/'
    failure_url = request.path_url.rpartition('/')[0] + '/edit'

    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
    instance =  context.create_subitem()
    dbsession = DBSession()
    fs = FieldSet(instance, session=dbsession)
    fs.rebind(instance, data=request.params)
    if fs.validate(): 
        fs.sync()
        dbsession.add(instance)
        return HTTPFound(location=success_url)
    return HTTPFound(location=failure_url)
    
def delete(context, request):
    success_url = context.parent_url(request)
    theme = Theme(context, request)
        
    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
    if 'form.button.confirm_delete' in request.params:
        dbsession = DBSession()
        dbsession.delete(context.model)
        return HTTPFound(location=success_url)
    return render('templates/delete.pt',
                  instance = context.model,
                  context = context,
                  request = request,
                  theme=theme,
                 )

