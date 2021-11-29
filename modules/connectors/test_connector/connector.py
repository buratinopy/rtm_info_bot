import logging

from modules.connectors import BaseConnector

logger = logging.getLogger("rtm.test_connector")


class TestConnector(BaseConnector):

    def connector(self, settings, **kwargs):
        logger.warning(settings)
