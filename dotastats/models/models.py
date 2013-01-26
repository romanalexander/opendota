from django.db import models

class SteamAccount: # Not a model, but still used.
    def __init__(self, values):
        self.values
        pass
    
    def __getattr__(self, attr):
        if attr in self.values:
          return self.values[attr]
        raise AttributeError("%r object has no attribute %r" % (type(self).__name__, attr))
        