from repoze.bfg.chameleon_zpt import render_template_to_response as render

import crud

def index(request):
    #types_list = get_registered_types().values()

    items = []
    #for ti in types_list:
    #    data = {
    #       'name' : ti.get('pretty_name_plural', 
    #             '%ss' % ti.get('pretty_name', ti['class'].__name__)),
    #       'slug' : ti['slug'],
    #    }
    #    items.append(data)

    #items.sort(lambda a,b: cmp(a['name'], b['name']))
    sections = crud.get_root().subsections
    return render('templates/home.pt',
                  request=request,
                  items = sections
                 )
