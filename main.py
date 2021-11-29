import logging
import time
import threading

import environment as env
from modules import scheduler
from modules import db_redis
from modules.bot.telegram_bot import start_tg_bot
from modules import prepare_logging
from modules.raptoreum_api import RaptoreumApi
from pycoingecko import CoinGeckoAPI

logger = logging.getLogger('rtm')
prepare_logging(logger=logger)

logger.info("Application started")


def init_apis():
    db_redis.init_db()
    env.rtm_api = RaptoreumApi()
    env.coingecko_api = CoinGeckoAPI()


def main():
    init_apis()

    scheduler.start_scheduler()

    tg_bot_thread = threading.Thread(
        target=start_tg_bot,
        daemon=True
    )
    tg_bot_thread.name = "tg_bot_thread"
    tg_bot_thread.start()
    logger.info("Start %s", tg_bot_thread.name)
    #
    # rtm_update_data_thread = threading.Thread(
    #     target=get_rtm_data,
    #     args=(env.redis,),
    #     daemon=True
    # )
    # rtm_update_data_thread.name = "rtm_update_data_thread"
    # rtm_update_data_thread.start()
    # logger.info("Start %s", rtm_update_data_thread.name)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
