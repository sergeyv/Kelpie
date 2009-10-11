from repoze.bfg.chameleon_zpt import render_template_to_response as render


def index(request):
    return render('templates/home.pt',
                  request=request,
                 )
