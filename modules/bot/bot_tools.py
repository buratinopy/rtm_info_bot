import logging
from datetime import datetime, timedelta

import orjson
from retry import retry

import environment as env
from modules import tofixed

logger = logging.getLogger('rtm.bot_tools')


def check_value(value):
    for ch in ['-', '+', 'e']:
        if ch in value:
            return False
    try:
        value = float(value)
    except ValueError:
        return False
    return value


def rtm(message):
    def render(**kwargs):
        tpl = f"""⚠ 𝗥𝗔𝗣𝗧𝗢𝗥𝗘𝗨𝗠 𝗜𝗡𝗙𝗢 ⚠
    📦 Block Height: {kwargs.get('blocks')}
    🛠 Difficulty: {kwargs.get('difficulty')}
    ⛏ Hashrate: {kwargs.get('networkmhashps')} MH/s
    💼 Available Supply: {kwargs.get('currentsupply')} RTM
    💲 24 Hours Price Change: 
                {kwargs.get('btc_24h_change')}% BTC
                {kwargs.get('ltc_24h_change')}% LTC
                {kwargs.get('usd_24h_change')}% USD
                {kwargs.get('rub_24h_change')}% RUB
    💵 Price: 
                {kwargs.get('pricesat')} Satoshi
                {kwargs.get('pricelit')} Litoshi
                {kwargs.get('priceusd')} USD
                {kwargs.get('pricerub')} RUB
    📊 24 Hours Volume: 
                {kwargs.get('vol24hbtc')} BTC
                {kwargs.get('vol24hltc')} LTC
                {kwargs.get('vol24husd')} USD
                {kwargs.get('vol24hrub')} RUB
    💰 Market Cap: {kwargs.get('marketcap')}
    ℹ Smartnodes: {kwargs.get('snenabled')} enabled / {kwargs.get('sntotal')} total
    🔒 Locked In Smartnodes: {kwargs.get('locked')}
        """
        return tpl

    logger.debug(message)
    last_execute = env.redis.get(f"last_execute_rtm_{message.chat.id}")
    if last_execute:
        env.bot.reply_to(message, f"Листай чат наверх. \n"
                                  f"У меня тут ограничение по частоте вызова этого метода для общих групп.\n"
                                  f"В личке - безлимит.")
        return
    data = env.redis.get("rtm_bot_data")
    report = render(**orjson.loads(data))
    env.bot.reply_to(message, report)
    constraint = env.settings['constraints']['method_call']['rtm']
    if message.chat.type != "private" \
            and (
            (isinstance(constraint['chats_allowed'], str) and constraint['chats_allowed'] == "all")
            or (isinstance(constraint['chats_allowed'], list) and message.chat.id in constraint['chats_allowed'])) \
            and constraint.get('time'):
        # TODO: переписать это говно в декоратор, что бы можно было ограничивать любые методы [1]
        env.redis.set(
            name=f"last_execute_rtm_{message.chat.id}",
            value=datetime.now().isoformat(),
            ex=timedelta(**constraint['time']).seconds
        )


@retry(Exception, tries=5, delay=1, logger=logger)
def rtm_calculate_coins_per_day(hashrate):
    data = env.redis.get("rtm_bot_data")
    rtm_info_cache = orjson.loads(data).get("mining_info_cache", {})
    networkhashps = float(rtm_info_cache.get('networkhashps', 0))
    coins_per_day = hashrate / networkhashps * 720 * 3750
    return coins_per_day


def check_achievement(chat_id):
    """
    Смотрим достижения чата (пока что только количество пользователей)
    :param chat_id:
    :return:
    """
    count_achievement = env.settings.get("events", {}).get("count_members", {}).get("count_achievement")
    if not count_achievement:
        logger.warning("events.count_members.count_achievement is not setup")
        return False, 0
    count_member = env.bot.get_chat_member_count(chat_id)
    if count_member % count_achievement == 0:
        return True, count_member
    return False, None


def pizdabol(message):
    return env.bot.send_photo(chat_id=message.chat.id,
                              reply_to_message_id=message.id,
                              photo="http://risovach.ru/upload/2013/05/mem/moe-lico_18461989_orig_.jpeg",
                              caption="Давай будем реалистами =)",
                              parse_mode='html')


def node_roi(message):
    constraint = env.settings['constraints']['method_call']['roi']
    # TODO: переписать это говно в декоратор, что бы можно было ограничивать любые методы [2]
    if message.chat.id < 0 and message.chat.id not in constraint['chats_allowed']:
        env.bot.reply_to(message,
                         text="Метод доступен только в личных сообщениях бота или в авторизованных группах.",
                         parse_mode='html')
        return
    roi_params = {
        "day": 1,
        "week": 7,
        "month": 30,
        "3month": 90,
        "6month": 180,
        "9month": 270,
        "annual": 365
    }
    return_message = "<b>Your profitability from {deposit} RTM in smartnode will be:</b>\n" \
                     "<b>😀 Day</b>: {day} RTM (+{day_percent}%)\n" \
                     "<b>😅 Week</b>: {week} RTM (+{week_percent}%)\n" \
                     "<b>🥳 Month</b>: {month} RTM (+{month_percent}%)\n" \
                     "<b>🤩 3 Month</b>: {3month} RTM (+{3month_percent}%)\n" \
                     "<b>🤑 6 Month</b>: {6month} RTM (+{6month_percent}%)\n" \
                     "<b>🏎 9 Month</b>: {9month} RTM (+{9month_percent}%)\n" \
                     "<b>🚀 Annual</b>: {annual} RTM (+{annual_percent}%)\n" \
                     "Service fee {fee}% is already included in the calculation.\n" \
                     "\n" \
                     "<b>Your profitability including reinvestment will be:</b>\n" \
                     "<b>😀 Day</b>: {day_reinvest} RTM (+{day_percent_reinvest}%)\n" \
                     "<b>😅 Week</b>: {week_reinvest} RTM (+{week_percent_reinvest}%)\n" \
                     "<b>🥳 Month</b>: {month_reinvest} RTM (+{month_percent_reinvest}%)\n" \
                     "<b>🤩 3 Month</b>: {3month_reinvest} RTM (+{3month_percent_reinvest}%)\n" \
                     "<b>🤑 6 Month</b>: {6month_reinvest} RTM (+{6month_percent_reinvest}%)\n" \
                     "<b>🏎 9 Month</b>: {9month_reinvest} RTM (+{9month_percent_reinvest}%)\n" \
                     "<b>🚀 Annual</b>: {annual_reinvest} RTM (+{annual_percent_reinvest}%)\n" \
                     "Service fee {fee}% is already included in the calculation.\n"

    args = message.text.lower().split(" ")

    def year_profit(deposit, required_node_deposit, fee=None):
        profit = 365 * 720 * (1000 * deposit / required_node_deposit) / shared_nodes_enabled
        if deposit < required_node_deposit:
            profit = profit - profit / 100 * fee
        year_percent = profit / deposit * 100
        return profit, year_percent

    if len(args) < 2 or not check_value(args[1]):
        env.bot.reply_to(message, "<b>Invalid argument!</b>\n"
                                  "Example of correct format: <b>/roi 10000</b>", parse_mode='html')
        return
    deposit = check_value(args[1])
    if deposit < 1000:
        env.bot.reply_to(message, "The iNodez does not work with deposits less than 1000 RTM", parse_mode='html')
        return

    if deposit > 100000000:
        pizdabol(message)
        return
    required_node_deposit = env.settings['required_node_deposit']
    rtm_data = orjson.loads(env.redis.get('rtm_bot_data'))
    shared_nodes_enabled = rtm_data.get("snenabled", 1)
    roi_result = {'deposit': deposit, 'fee': 0}
    for k, days in roi_params.items():
        profitability = days * 720 * (1000 * deposit / required_node_deposit) / shared_nodes_enabled
        if deposit < required_node_deposit:
            profitability = profitability - profitability / 100 * 6
            roi_result['fee'] = 6
        if not profitability % 10:
            roi_result[k] = tofixed(profitability, 0)
        else:
            roi_result[k] = tofixed(profitability, 3)
        roi_result[f'{k}_percent'] = tofixed(profitability / deposit * 100, 2)

    _, year_percent = year_profit(deposit, required_node_deposit, 6)
    for k, days in roi_params.items():
        reinvest_profitability = deposit * (1 + year_percent / 100 / 365) ** days - deposit
        roi_result[f'{k}_reinvest'] = tofixed(reinvest_profitability, 3)
        roi_result[f'{k}_percent_reinvest'] = tofixed(reinvest_profitability / deposit * 100, 2)

    env.bot.reply_to(message, return_message.format(**roi_result), parse_mode='html')


def convert(message):
    args = message.text.lower().split(" ")

    if len(args) < 2 or not check_value(args[1]):
        env.bot.reply_to(message, "<b>Invalid argument!</b>\n"
                                  "Example of correct format: <b>/convert 10000</b>", parse_mode='html')
        return
    balance = check_value(args[1])
    if balance > 21000000000:
        pizdabol(message)
        return
    convert_map = {
        'Satoshi': 'pricesat',
        'Litoshi': 'pricelit',
        'USD': 'priceusd',
        'RUB': 'pricerub'
    }

    rtm_data = orjson.loads(env.redis.get('rtm_bot_data'))
    price = {}
    convert_balance = {}
    for currency, keyname in convert_map.items():
        price[keyname] = float(rtm_data.get(keyname, 0))
        convert_balance[keyname] = tofixed(price.get(keyname) * balance, 3)
    return_message = f"""
💵 <b>Price RTM on the CoinGecko:</b> 
        1 RTM == {price.get('pricesat')} Satoshi
        1 RTM == {price.get('pricelit')} Litoshi
        1 RTM == {price.get('priceusd')} USD
        1 RTM == {price.get('pricerub')} RUB
💵 <b>Converted balance:</b>
        Your {balance} RTM ~= {convert_balance.get('priceusd')} USD
        Your {balance} RTM ~= {convert_balance.get('pricerub')} RUB
"""
    env.bot.reply_to(message, return_message, parse_mode='html')


def chat_dialog(message):
    if not env.settings['dialog']['enable']:
        return
    for rule in env.settings['dialog']['rules']:
        for stop_word in rule.get('stop_words', []):
            if stop_word.lower() in str(message.text).lower():
                env.bot.reply_to(message, rule['replay'].format(stop_word=stop_word))


def new_member(message):
    """
    Записываем нового пользователя группы в бд
    """
    for new_chat_member in message.json['new_chat_members']:
        if not new_chat_member['is_bot'] and \
                not env.redis.get(f"user_{new_chat_member['id']}"):
            new_user = dict(
                id=new_chat_member['id'],
                username=new_chat_member.get('username'),
                first_name=new_chat_member.get('first_name'),
                last_name=new_chat_member.get('last_name'),
                chat_id=message.chat.id,
                chat_title=message.chat.title,
                chat_name=message.chat.username,
                invite_link=message.chat.invite_link,
                date=message.json['date'],
                date_dt=datetime.fromtimestamp(message.json['date']).isoformat(),
            )
            logger.info("New user_%s_%s: %s", message.chat.id, new_chat_member['id'], new_user)
            env.redis.set(
                f"user_{message.chat.id}_{new_chat_member['id']}",
                orjson.dumps(new_user)
            )
            if not env.settings.get('events', {}).get('enable'):
                return
            # смотрим, сколько участников и радуемся, если достигли кратности из кофнфига
            achievement, count_member = check_achievement(message.chat.id)
            if achievement:
                env.bot.send_photo(chat_id=message.chat.id,
                                   photo='https://pbs.twimg.com/media/CbxUOadW8AEj1Ha.jpg',
                                   caption=f"Армия адептов RTM растёт! Нас уже {count_member}!",
                                   parse_mode="html")
    return
