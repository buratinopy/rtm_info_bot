from redis import Redis
from redis import ConnectionPool

import environment as env


def init_db():
    env.redis = Redis(connection_pool=ConnectionPool(**env.settings['redis']))
