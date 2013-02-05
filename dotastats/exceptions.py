class SteamAPIError(Exception):
    """  Error raised when the Steam API has issues. """
    def __init__(self, value):
        self.errormessage = value