from repoze.bfg.chameleon_zpt import render_template_to_response as render
from webob.exc import HTTPFound

from formalchemy import FieldSet

from kelpie.models import DBSession
from kelpie.models import ZopeInstance

def list_all(request):
    dbsession = DBSession()
    instances = dbsession.query(ZopeInstance).all()
    return render('templates/zope_instances/list_all.pt',
                  instances = instances,
                  request = request,
                 )
                                       
def view(request):
    id = request.matchdict['item_id']
    dbsession = DBSession()
    instance = dbsession.query(ZopeInstance).filter(ZopeInstance.id==id).one()
    return render('templates/zope_instances/view.pt',
                   instance = instance,
                   request = request,
                  )

def edit(request):
    id = request.matchdict['item_id']
    dbsession = DBSession()
    instance = dbsession.query(ZopeInstance).filter(ZopeInstance.id==id).one()
    fs = FieldSet(instance)
    return render('templates/zope_instances/edit.pt',
                  instance = instance,
                  form = fs.render(),
                  request = request,
                 )

def add(request):
    dbsession = DBSession()
    instance =  ZopeInstance()
    fs = FieldSet(instance, session=dbsession)
    return render('templates/zope_instances/add.pt',
                  instance = instance,
                  form = fs.render(),
                  request = request,
                 )

def save(request):
    id = request.matchdict.get('item_id', None)
    dbsession = DBSession()
    if id:
        instance = dbsession.query(ZopeInstance).filter(ZopeInstance.id==id).one()
    else:
        instance = ZopeInstance()
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
    if 'form.button.confirm_delete' in request.params:
        id = request.matchdict.get('item_id', None)
        dbsession = DBSession()
        instance = dbsession.query(ZopeInstance).filter(ZopeInstance.id==id).one()
        dbsession.delete(instance)
        #instance.save()
        success_url = '/zopes/'
        return HTTPFound(location=success_url)

    return render('templates/zope_instances/delete.pt',
                  instance = instance,
                  request = request,
                 )

