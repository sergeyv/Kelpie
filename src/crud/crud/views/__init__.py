from repoze.bfg.chameleon_zpt import render_template_to_response as render
from webob.exc import HTTPFound

from formalchemy import FieldSet

from kelpie.models import DBSession

from crud import get_content_type

def index(request):
    slug = request.matchdict['content_type_slug']
    cti = get_content_type(slug)
    if cti is None:
        raise NotFound
    dbsession = DBSession()
    instances = dbsession.query(cti['class']).all()
    return render(template_name,
                  instances = instances,
                  request = request,
                 )
                                       
def view(request,cls,template_name):
    id = request.matchdict['item_id']
    dbsession = DBSession()
    instance = dbsession.query(cls).filter(cls.id==id).one()
    return render(template_name,
                   instance = instance,
                   request = request,
                  )

def edit(request, cls):
    id = request.matchdict['item_id']
    dbsession = DBSession()
    instance = dbsession.query(cls).filter(cls.id==id).one()
    fs = FieldSet(instance)
    return render('templates/zope_instances/edit.pt',
                  instance = instance,
                  form = fs.render(),
                  request = request,
                 )

def add(request,cls):
    dbsession = DBSession()
    instance =  cls()
    fs = FieldSet(instance, session=dbsession)
    return render('templates/zope_instances/add.pt',
                  instance = instance,
                  form = fs.render(),
                  request = request,
                 )

def save(request,cls,success_url):
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

    
def delete(request, cls, success_url):

    if 'form.button.cancel' in request.params:
        return HTTPFound(location=success_url)
        
    id = request.matchdict.get('item_id', None)
    dbsession = DBSession()
    instance = dbsession.query(cls).filter(cls.id==id).one()
    if 'form.button.confirm_delete' in request.params:
        dbsession.delete(instance)
        #instance.save()
        return HTTPFound(location=success_url)

    return render('templates/zope_instances/delete.pt',
                  instance = instance,
                  request = request,
                 )

