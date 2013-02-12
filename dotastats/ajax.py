from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.template.loader import render_to_string
from dotastats.models import Heroes

@dajaxice_register
def search_matches(request, search_request):
    if len(search_request) < 2:
        return None
    dajax = Dajax()
    dajax.add_data("<tr><td>TestData</td></tr>", 'render_matches')
    return dajax.json()

@dajaxice_register
def search_players(request, search_request):
    if len(search_request) < 2:
        return None
    dajax = Dajax()
    dajax.add_data("<tr><td>TestData</td></tr>", 'render_players')
    return dajax.json()

@dajaxice_register
def search_heroes(request, search_request):
    if len(search_request) < 2:
        return None
    dajax = Dajax()
    result_set = Heroes.objects.filter(dota2_name__icontains=search_request)[:25]
    result_string = render_to_string('ajax/search_results_hero.html', dictionary=dict({'results': result_set}))    
    dajax.add_data(result_string, 'render_heroes')
    return dajax.json()
