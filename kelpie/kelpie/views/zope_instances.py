from repoze.bfg.chameleon_zpt import render_template_to_response as render

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
    id = request.matchdict['instance']
    dbsession = DBSession()
    instance = dbsession.query(ZopeInstance).filter(ZopeInstance.id==id).one()
    return render('templates/zope_instances/view.pt',
                   instance = instance,
                   request = request,
                  )

def edit(request):
    id = request.matchdict['instance']
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
    fs = FieldSet(ZopeInstance)
    return render('templates/zope_instances/add.pt',
                  form = fs.render(),
                  request = request,
                 )

