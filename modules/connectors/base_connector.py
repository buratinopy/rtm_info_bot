import logging
from typing import Dict
from datetime import datetime
from modules import get_settings
from modules.exceptions import SettingsFileNotExistError
import environment as env

logger = logging.getLogger("rtm.base_connector")


class ConnectorError(Exception):
    pass


class ErrorNotExitsRequiredParameter(Exception):
    pass


class BaseConnector:
    """Base connector class"""
    default_module_config = ''
    required_parameters = frozenset([])

    @staticmethod
    def format_time(time: datetime, time_format: str) -> str:
        return time.strftime(time_format)

    def connector(self, settings, **kwargs):
        # Your connector
        pass

    def start(self, settings, **kwargs):
        def import_config(_settings: dict) -> Dict:
            """ Импорт данных кастомного конфига из правила для переопределения значений базового конфига """
            if _settings.get('connector_params'):
                try:
                    _settings.update(get_settings(_settings['connector_params']))
                except SettingsFileNotExistError as err:
                    logger.error("[%s] - %s", _settings['rule_name'], err)
                    raise SettingsFileNotExistError
            _settings.pop('connector_params')
            return _settings

        if self.default_module_config:
            default_settings = env.get_settings(self.default_module_config)
            if default_settings:
                settings = {**default_settings, **import_config(settings)}
            else:
                settings = import_config(settings)

        for key in self.required_parameters:
            if key not in settings:
                logger.error("[%s] - Not exist required parameter %s", settings['rule_name'], key)
                raise ErrorNotExitsRequiredParameter
        try:
            self.connector(settings, **kwargs)
        except Exception as err:
            raise ConnectorError(err)
