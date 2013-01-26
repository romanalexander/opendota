from django.shortcuts import render
from dotastats.json import steamapi

def home(request):
    return render(request, 'home.html')
    
def matches_overview(request):
    result_dict = steamapi.GetMatchHistory()
    return render(request, 'match_history.html', result_dict)

def matches_id(request, match_id):    
    return render(request, 'match_id.html')
