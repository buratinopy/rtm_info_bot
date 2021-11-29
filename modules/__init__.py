import os
import logging
from typing import Dict, NoReturn

import yaml
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler

logger = logging.getLogger('rtm_tools')


def get_settings(settings_file='appconfig/setting.yaml'):
    """
        Получение конфигурации из yaml файла.
    """
    settings_path = os.path.join(os.getcwd(), settings_file)
    if not os.path.exists(settings_path):
        logger.error(f'Error getting setting. Check your settings file in {settings_path}')
        raise Exception(f"File {settings_path} doesn't exist")
    with open(settings_path, encoding='utf-8') as f:
        setting = yaml.load(f.read(), Loader=yaml.FullLoader)
    logger.debug('settings loaded: {}'.format(settings_path))
    return setting


def prepare_logging(settings: Dict = None, logger: logging.Logger = None) -> NoReturn:
    """
    Метод подготовки логгера
    :param settings: настройки сервиса, в первую очередь те, что касаются логирования
    :param logger: экземпляр класса логгера сервиса
    :return:
    """
    if not logger:
        return None  # нет логгера - нет логов
    if settings is None:
        settings = {'logging': {'basic_level': "DEBUG", 'term_level': "DEBUG"}}

    logger.setLevel(settings['logging']['basic_level'])
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(settings['logging']['term_level'])
    stream_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(levelname)-s - %(name)-20s - '
            '[in %(pathname)s:%(lineno)d]: - %(message)s')
    )
    logger.addHandler(stream_handler)
    if settings.get('sentry_url'):
        sentry_handler = SentryHandler(settings['sentry_url'])
        sentry_handler.setLevel(settings['logging']['sentry_level'])
        setup_logging(sentry_handler)
        logger.addHandler(sentry_handler)


def tofixed(num: float, digits=0):
    return f"{num:.{digits}f}"

