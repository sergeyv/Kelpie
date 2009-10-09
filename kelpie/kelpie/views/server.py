from repoze.bfg.chameleon_zpt import render_template_to_response as render

from formalchemy import FieldSet

from kelpie.models import DBSession
from kelpie.models import Server

def list_all(request):
    dbsession = DBSession()
    items = dbsession.query(Server).all()
    return render('templates/servers/list_all.pt',
                  items = items,
                  request = request,
                 )
                                       
def view(request):
    id = request.matchdict['item_id']
    dbsession = DBSession()
    item = dbsession.query(Server).filter(Server.id==id).one()
    return render('templates/servers/view.pt',
                   item = item,
                   request = request,
                  )

def edit(request):
    id = request.matchdict['item_id']
    dbsession = DBSession()
    item = dbsession.query(Server).filter(Server.id==id).one()
    fs = FieldSet(instance)
    return render('templates/servers/edit.pt',
                  item = item,
                  form = fs.render(),
                  request = request,
                 )

def add(request):
    dbsession = DBSession()
    fs = FieldSet(Server)
    return render('templates/servers/add.pt',
                  form = fs.render(),
                  request = request,
                 )

