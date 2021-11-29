from .base_connector import BaseConnector
from .test_connector.connector import TestConnector
from .informer.connector import TgInformer
from .rtm_info_data.connector import RtmDataCache

connectors_map = {
    "test_connector": TestConnector,
    "informer": TgInformer,
    "rtm_info_data": RtmDataCache,
}
