
from repoze.bfg.chameleon_zpt import render_template_to_response as render
from webob.exc import HTTPFound

from formalchemy import FieldSet

from crud.models import DBSession

from crud import get_typeinfo_by_slug
from crud import IModel

def index(context,request):
    dbsession = DBSession()
    cls = context.typeinfo['class']
    instances = dbsession.query(cls).all()
    return render('templates/index.pt',
                  context=context,
                  instances = instances,
                  request = request,
                 )
                                       
def view(context, request):
    return render('templates/view.pt',
                   instance = context,
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
    cls = context.typeinfo['class']
    instance =  cls()
    fs = FieldSet(instance, session=dbsession)
    return render('templates/add.pt',
                  instance = instance,
                  context = context,
                  form = fs.render(),
                  request = request,
                 )

def save(context, request):
    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
    existing = IModel.providedBy(context)
    if existing:
        instance = context
    else:
        cls = context.typeinfo['class']
        instance = cls()
    dbsession = DBSession()
    fs = FieldSet(instance, session=dbsession)
    fs.rebind(instance, data=request.params)
    if fs.validate(): fs.sync()
    if not existing:
        dbsession.add(instance)
    #instance.save()
    success_url = request.path_url.rpartition('/')[0]+ '/'
    failure_url = request.path_url.rpartition('/')[0] + '/edit'
    return HTTPFound(location=success_url)

    
def delete(context, request):
    success_url = request.path_url.rpartition('/')[0]+ '/'
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

