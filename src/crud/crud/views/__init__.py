
from repoze.bfg.chameleon_zpt import render_template_to_response as render
from repoze.bfg import traversal

from webob.exc import HTTPFound
from formalchemy import FieldSet
from crud.models import DBSession

from crud import IModel, ISection, ModelProxy

def index(context,request):
    # context is a Section object here
    dbsession = DBSession()
    
    instances = context.get_items()
    return render('templates/index.pt',
                  context=context,
                  instances = instances,
                  request = request,
                 )
                                       
def view(context, request):
    #context is ModelProxy here
    dbsession = DBSession()
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
                  )

def edit(context, request):
    # context is ModelProxy here
    fs = FieldSet(context.model)
    return render('templates/edit.pt',
                  context = context,
                  form = fs.render(),
                  request = request,
                 )

def add(context, request):
    # context is Section here
    dbsession = DBSession()
    item_class = context.get_subitems_class()
    instance =  item_class()
    fs = FieldSet(instance, session=dbsession)
    return render('templates/add.pt',
                  instance = instance,
                  context = context,
                  form = fs.render(),
                  request = request,
                 )

def save(context, request):
    success_url = request.path_url.rpartition('/')[0]+ '/'
    failure_url = request.path_url.rpartition('/')[0] + '/edit'

    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
    existing = IModel.providedBy(context)
    if existing:
        instance = context.model
    else:
        item_class = context.get_subitems_class()
        instance =  item_class()
    dbsession = DBSession()
    fs = FieldSet(instance, session=dbsession)
    fs.rebind(instance, data=request.params)
    if fs.validate(): fs.sync()
    if not existing:
        dbsession.add(instance)
    #instance.save()
    return HTTPFound(location=success_url)

    
def delete(context, request):
    my_section = traversal.find_interface(context, ISection)
    if my_section:
        success_url = my_section.url(request)
    else:
        success_url = request.application_url
        
    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
    if 'form.button.confirm_delete' in request.params:
        dbsession = DBSession()
        dbsession.delete(context.model)
        return HTTPFound(location=success_url)
    return render('templates/delete.pt',
                  instance = context.model,
                  request = request,
                 )

