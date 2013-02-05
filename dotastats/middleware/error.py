from django.shortcuts import render
from dotastats.exceptions import SteamAPIError

class SteamErrorMiddleware(object):
    def process_exception(self, request, exception):
        try:
            if isinstance(exception, SteamAPIError):
                return render(request, '500.html', {'error': 'SteamAPI: ' + exception.errormessage})
        except: # Need to ignore all errors here, or we'll get stuck in loop.
            pass
        return None