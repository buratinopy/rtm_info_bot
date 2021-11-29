import logging
import time

import environment as env
from modules.connectors import BaseConnector

logger = logging.getLogger("rtm.telegram_informer")


class TgInformer(BaseConnector):
    @staticmethod
    def send_info_message(rule):
        if rule.get('chats'):
            chats = rule['chats']
        else:
            chats = env.settings['chats']
        for chat_id in chats:
            env.bot.send_photo(chat_id=chat_id,
                               photo=rule.get('photo'),
                               caption=rule.get('message'),
                               parse_mode="html")
            time.sleep(1)  # что бы тележка не ругалась

    def connector(self, settings, **kwargs):
        connector_params = settings['connector_params']
        self.send_info_message(connector_params)
        logger.warning(connector_params)
