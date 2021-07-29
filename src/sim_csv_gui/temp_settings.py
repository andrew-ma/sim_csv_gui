class TempSettings:
    """This uses the same interface as QSettings() so it can be substituted later
    But this stores only temporarily in memory without persistence
    """

    def __init__(self):
        self._settings_dict = {}

    def setValue(self, key, value):
        self._settings_dict[key] = value

    def value(self, key, defaultValue=None):
        return self._settings_dict.get(key, defaultValue)

    def status(self):
        return 0

    def sync(self):
        pass
