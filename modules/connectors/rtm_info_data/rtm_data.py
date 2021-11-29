import logging
from multiprocessing.pool import ThreadPool
import time

import json
from datetime import datetime
from retry import retry
from modules import tofixed
import environment as env

logger = logging.getLogger("rtm.rtm_data")


@retry(Exception, tries=5, delay=2, backoff=2, logger=logger)
def mining_info():
    _mining_info = env.rtm_api.get_mining_info()
    blocks = _mining_info.get('blocks', None)
    difficulty = tofixed(float(_mining_info.get('difficulty', 0.0)), 3)
    networkmhashps = tofixed(float(_mining_info.get('networkhashps', 0.0)) / 1000000, 3)
    return _mining_info, blocks, difficulty, networkmhashps


@retry(Exception, tries=5, delay=2, backoff=2, logger=logger)
def get_currentsupply():
    return tofixed(env.rtm_api.supply())


@retry(Exception, tries=5, delay=2, backoff=2, logger=logger)
def get_marketcap():
    return env.rtm_api.marketcap()


@retry(Exception, tries=5, delay=2, backoff=2, logger=logger)
def smartnode():
    _snenabled = env.rtm_api.smartnode("count")
    snenabled = _snenabled.get('enabled', 0)
    sntotal = _snenabled.get('total', 0)
    locked = env.rtm_api.gettotallockedcoins()
    return snenabled, sntotal, locked


@retry(Exception, tries=5, delay=2, backoff=2, logger=logger)
def get_price_bts():
    _pricebtc = env.coingecko_api.get_price(ids='raptoreum', vs_currencies='btc', include_24hr_vol=True,
                                            include_24hr_change=True)
    pricesat = tofixed(_pricebtc.get('raptoreum', {}).get('btc', 0) * 100000000, 1)
    vol24hbtc = tofixed(_pricebtc.get('raptoreum', {}).get('btc_24h_vol', 0), 3)
    btc_24h_change = tofixed(_pricebtc.get('raptoreum', {}).get('btc_24h_change', 1))
    return pricesat, vol24hbtc, btc_24h_change


@retry(Exception, tries=5, delay=2, backoff=2, logger=logger)
def get_price_ltc():
    _priceltc = env.coingecko_api.get_price(ids='raptoreum', vs_currencies='ltc', include_24hr_vol=True,
                                            include_24hr_change=True)
    pricelit = tofixed(_priceltc.get('raptoreum', {}).get('ltc', 0) * 100000000, 1)
    vol24hltc = tofixed(_priceltc.get('raptoreum', {}).get('ltc_24h_vol', 0))
    ltc_24h_change = tofixed(_priceltc.get('raptoreum', {}).get('ltc_24h_change', 1))
    return pricelit, vol24hltc, ltc_24h_change


@retry(Exception, tries=5, delay=2, backoff=2, logger=logger)
def get_price_usd():
    _priceusd = env.coingecko_api.get_price(ids='raptoreum', vs_currencies='usd', include_24hr_vol=True,
                                            include_24hr_change=True)
    priceusd = tofixed(_priceusd.get('raptoreum', {}).get('usd', 0), 5)
    vol24husd = tofixed(_priceusd.get('raptoreum', {}).get('usd_24h_vol', 0))
    usd_24h_change = tofixed(_priceusd.get('raptoreum', {}).get('usd_24h_change', 1))
    return priceusd, vol24husd, usd_24h_change


@retry(Exception, tries=5, delay=2, backoff=2, logger=logger)
def get_price_rub():
    _pricerub = env.coingecko_api.get_price(ids='raptoreum', vs_currencies='rub', include_24hr_vol=True,
                                            include_24hr_change=True)
    pricerub = tofixed(_pricerub.get('raptoreum', {}).get('rub', 0), 3)
    vol24hrub = tofixed(_pricerub.get('raptoreum', {}).get('rub_24h_vol', 0))
    rub_24h_change = tofixed(_pricerub.get('raptoreum', {}).get('rub_24h_change', 1))
    return pricerub, vol24hrub, rub_24h_change


def update_rtm_data_cache(redis_connection):
    t1 = datetime.now()

    pool = ThreadPool(processes=8)
    mining_info_result = pool.apply_async(mining_info)
    currentsupply_result = pool.apply_async(get_currentsupply)
    marketcap_result = pool.apply_async(get_marketcap)
    smartnode_result = pool.apply_async(smartnode)
    price_bts_result = pool.apply_async(get_price_bts)
    price_ltc_result = pool.apply_async(get_price_ltc)
    price_usd_result = pool.apply_async(get_price_usd)
    price_rub_result = pool.apply_async(get_price_rub)

    mining_info_cache, blocks, difficulty, networkmhashps = mining_info_result.get()
    mining_info_cache['_service_dict'] = True
    currentsupply = currentsupply_result.get()
    marketcap = marketcap_result.get()
    snenabled, sntotal, locked = smartnode_result.get()
    pricesat, vol24hbtc, btc_24h_change = price_bts_result.get()
    pricelit, vol24hltc, ltc_24h_change = price_ltc_result.get()
    priceusd, vol24husd, usd_24h_change = price_usd_result.get()
    pricerub, vol24hrub, rub_24h_change = price_rub_result.get()

    variables = {}
    for k, v in vars().items():
        if type(v) in [str, float, int] \
                or (type(v) == dict and v.get('_service_dict', False)):
            variables[k] = v
    redis_connection.set("rtm_bot_data", json.dumps(variables))
    pool.close()

    t2 = datetime.now()
    logger.info("Updated RTM data [execution_time: %s]: %s", t2 - t1, variables)


def get_rtm_data(redis_connection):
    while True:
        update_rtm_data_cache(redis_connection)
        time.sleep(120)
