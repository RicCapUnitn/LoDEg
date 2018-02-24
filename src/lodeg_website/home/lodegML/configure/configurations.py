class DefaultConfigurationsHolder():

    _configs = {
        'default': {
            'query_mem_opt': True,
            'keep_user_info': True,
            'keep_session_data': False,
            'ml_mem_opt': False,
            'ml_autorun': True,
            'plot_target': 'web',
            'cache': None,
            'debug': True
        },
        'low_mem': {
            'query_mem_opt': True,
            'keep_user_info': False,
            'keep_session_data': False,
            'ml_mem_opt': True,
            'ml_autorun': False,
            'plot_target': 'web',
            'cache': None,
            'debug': True
        },
        'console': {
            'query_mem_opt': True,
            'keep_user_info': True,
            'keep_session_data': False,
            'ml_mem_opt': False,
            'ml_autorun': False,
            'plot_target': 'console',
            'cache': None,
            'debug': True
        },
        'web': {
            'query_mem_opt': True,
            'keep_user_info': True,
            'keep_session_data': False,
            'ml_mem_opt': True,
            'ml_autorun': False,
            'plot_target': 'web',
            'cache': 'sqlite',  # Default should be set to None or be always available,
            'debug': True
        }
    }

    def get(self, configuration):
        try:
            config = self._configs[configuration]
        except KeyError:
            config = self._configs['default']
        return config.copy()
