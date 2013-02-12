from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from dotastats.json import steamapi
from django.views.decorators.cache import cache_page

def home(request):
    return render(request, 'home.html')

@cache_page(60 * 1)
def matches_overview(request):
    match_history_list = steamapi.GetLatestMatches()
    paginator = Paginator(match_history_list, 25)
    
    page = request.GET.get('page')
    try:
        match_history = paginator.page(page)
    except PageNotAnInteger:
        match_history = paginator.page(1)
    except EmptyPage:
        match_history = paginator.page(paginator.num_pages)
    
    return render(request, 'match_history.html', {'match_history': match_history})

@cache_page(60 * 5)
def matches_id(request, match_id):
    result_match = steamapi.GetMatchDetails(match_id)
    return render(request, 'match_id.html', {'match': result_match, 'teams': (result_match.get_radiant_players(), result_match.get_dire_players())})

def about(request):
    return render(request, 'about.html')

def news(request):
    return render(request, 'news.html')

def leagues(request):
    return render(request, 'leagues.html')

# Ajax Polymorphic search provider. Consider using Haystack instead of internal.
def search(request, search_param=None):
    error = None
    if search_param == None:
        search_param = ""
    if len(search_param) < 2:
        error = "Search query too short. Please add more keywords."
    result_dict = dict({'error': error, 
                        'search_param': search_param})
    return render(request, 'search.html', result_dict)

def heroes(request, hero_name=None):
    return render(request, 'heroes.html')

def players(request, player_id=None, player_url=None):
    return render(request, 'players.html')

