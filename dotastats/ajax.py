from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

# TODO: Use django-celery for parallelization.

@dajaxice_register
def search_matches(request, search_request):
    dajax = Dajax()
    dajax.add_data("<tr><td>TestData</td></tr>", 'parse_matches')
    return dajax.json()

@dajaxice_register
def search_players(request, search_request):
    dajax = Dajax()
    dajax.add_data("<tr><td>TestData</td></tr>", 'parse_players')
    return dajax.json()

@dajaxice_register
def search_heroes(request, search_request):
    dajax = Dajax()
    dajax.add_data("<tr><td>TestData</td></tr>", 'parse_heroes')
    return dajax.json()
