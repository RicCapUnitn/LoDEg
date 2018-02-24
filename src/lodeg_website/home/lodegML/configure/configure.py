from configure.configurations import DefaultConfigurationsHolder  # migrate


class SystemConfigs():

    def __init__(self, modality='default'):
        self._configuration_holder = DefaultConfigurationsHolder()
        self._configuration = self._configuration_holder.get(modality)

    def __getitem__(self, item):
        return self._configuration[item]

    def __setitem__(self, key, value):
        self._configuration[key] = value

    def __contains__(self, key):
        return key in self._configuration

    def __eq__(self, other):
        if isinstance(other, dict.__class__):
            for key in self._configuration:
                if key not in other.keys():
                    return False
                else:
                    if self._configuration[key] != other[key]:
                        return False
            return True
        else:
            return False

    def getSettings(self):
        return self._configuration.copy()
