from repoze.bfg.chameleon_zpt import render_template_to_response as render
from webob.exc import HTTPFound

from formalchemy import FieldSet

from crud.models import DBSession

from crud import get_content_type

def index(context,request):
    dbsession = DBSession()
    instances = dbsession.query(context.cls).all()
    return render('templates/index.pt',
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
    instance =  context.cls()
    fs = FieldSet(instance, session=dbsession)
    return render('templates/add.pt',
                  instance = instance,
                  form = fs.render(),
                  request = request,
                 )

def save(context, request):
    slug = request.matchdict['content_type_slug']
    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
    id = request.matchdict.get('item_id', None)
    dbsession = DBSession()
    if id:
        instance = dbsession.query(cls).filter(cls.id==id).one()
    else:
        instance = cls()
    fs = FieldSet(instance)
    fs.rebind(instance, data=request.params)
    if fs.validate(): fs.sync()
    if not id:
        dbsession.add(instance)
    #instance.save()
    success_url = request.path_url.rpartition('/')[0]+ '/'
    failure_url = request.path_url.rpartition('/')[0] + '/edit'
    return HTTPFound(location=success_url)

    
def delete(request):
    slug = request.matchdict['content_type_slug']
    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
        
    id = request.matchdict.get('item_id', None)
    dbsession = DBSession()
    instance = dbsession.query(cls).filter(cls.id==id).one()
    if 'form.button.confirm_delete' in request.params:
        dbsession.delete(instance)
        #instance.save()
        return HTTPFound(location=success_url)

    return render('templates/delete.pt',
                  instance = instance,
                  request = request,
                 )

