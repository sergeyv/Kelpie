
from repoze.bfg.chameleon_zpt import render_template_to_response as render
from repoze.bfg import traversal

from webob.exc import HTTPFound
from formalchemy import FieldSet
from crud.models import DBSession

from crud import get_typeinfo_by_slug
from crud import IModel

def index(context,request):
    dbsession = DBSession()
    #cls = context.typeinfo['class']
    
    instances = dbsession.query(context.class_).all()
    return render('templates/index.pt',
                  context=context,
                  instances = instances,
                  request = request,
                 )
                                       
def view(context, request):
    fs = FieldSet(context)
    include = []
    for (k, field) in fs.render_fields.items():
        include.append(field.readonly())
    fs.configure(include=include)
    return render('templates/view.pt',
                   instance = context,
                   form = fs.render(),
                   request = request,
                  )

def edit(context, request):
    fs = FieldSet(context)
    return render('templates/edit.pt',
                  instance = context,
                  form = fs.render(),
                  request = request,
                 )

def add(context, request):
    dbsession = DBSession()
    instance =  context.class_()
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
        instance = context
    else:
        instance = context.class_()
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
        success_url = my_section.section_url(request)
    else:
        success_url = request.application_url
        
    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
    if 'form.button.confirm_delete' in request.params:
        dbsession = DBSession()
        dbsession.delete(context)
        return HTTPFound(location=success_url)
    return render('templates/delete.pt',
                  instance = context,
                  request = request,
                 )

