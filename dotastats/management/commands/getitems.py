from django.core.management.base import BaseCommand, CommandError
from dotastats.models import Items
import re

class Command(BaseCommand):
    args = ''
    help = 'Initializes item list from root\scripts\npc\item.txt'

    def handle(self, *args, **options):
        file = open('resources/items.txt')
        key = None
        value = None
        item_list = [Items(pk=0, client_name='item_None')]
        for textline in file:
            rg = re.compile('("ID")'+'.*?'+'(\\d+)',re.IGNORECASE|re.DOTALL)
            m = rg.search(textline)
            if m:
                string1=m.group(1)
                int1=m.group(2)
                key = int1
            rg = re.compile('("AbilityName")'+'.*?'+'((?:[a-z][a-z0-9_]*))',re.IGNORECASE|re.DOTALL)
            m = rg.search(textline)
            if m:
                string1=m.group(1)
                var1=m.group(2)
                value = var1
                
            if key and value:
                item_list.append(Items(pk=key, client_name=value))
                key = None
                value = None
        if len(item_list) == 0:
            raise CommandError("Didn't import any items.")
        Items.objects.bulk_create(item_list)
        self.stdout.write('Successfully imported items.\n')
