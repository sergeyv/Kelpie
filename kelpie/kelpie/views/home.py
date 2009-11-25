from repoze.bfg.chameleon_zpt import render_template_to_response as render

import crud

def index(request):
    sections = crud.get_root().subsections
    return render('templates/home.pt',
                  request=request,
                  items = sections
                 )
