from repoze.bfg.chameleon_zpt import render_template_to_response as render
from webob.exc import HTTPFound

from formalchemy import FieldSet

from kelpie.models import DBSession
from kelpie.models import Server
from kelpie.models import crud

def index(request):
    return crud.index(request, Server, 'templates/servers/index.pt')
                                       
def view(request):
    return crud.view(request, Server, 'templates/servers/view.pt')

def edit(request):
    return crud.edit(request, Server)

def add(request):
    return crud.add(request, Server)

def save(request):
    return crud.save(request, Server, success_url='/servers')
    
def delete(request):
    return crud.save(request, Server, success_url='/servers')
