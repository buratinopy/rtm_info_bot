import logging
import time

import environment as env
from modules.connectors import BaseConnector
from modules.connectors.rtm_info_data.rtm_data import update_rtm_data_cache

logger = logging.getLogger("rtm.rtm_info_data")


class RtmDataCache(BaseConnector):
    def connector(self, settings, **kwargs):
        update_rtm_data_cache(env.redis)
