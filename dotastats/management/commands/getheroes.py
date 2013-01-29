from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from dotastats.models import Heroes
import simplejson as json
import urllib
import urllib2

API_KEY = settings.STEAM_API_KEY
HEROES_URL = 'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/'
class Command(BaseCommand):
    args = ''
    help = 'Initializes heroes list from Steam servers.'

    def handle(self, *args, **options):
        try: # TODO: Other localizations.
            hero_list = []
            kargs = dict({'key': API_KEY, 'language': 'en_us'})
            url_data = urllib.urlencode(kargs)
            response = urllib2.urlopen(HEROES_URL + '?' + url_data)
            json_data = json.loads(response.read())['result']
            response.close()
            for hero in json_data['heroes']:
                hero_list.append(Heroes(hero_id=hero['id'],
                                    client_name=hero['name'],
                                    dota2_name=hero['localized_name'],
                                    ))
            if len(hero_list) == 0:
                raise CommandError("Didn't find any heroes to import.")
            Heroes.objects.bulk_create(hero_list)
            self.stdout.write('Successfully imported heroes.\n')
        except urllib2.HTTPError, e:
            if e.code == 400:
                json_data.update({'error': 'Malformed request.'})
            elif e.code == 401:
                json_data.update({'error': 'Unauthorized API access.'})
            elif e.code == 503:
                json_data.update({'error': 'Steam servers overloaded.'})
            else:
                json_data.update({'error': 'Unknown HTTP error' + e.code})
        return