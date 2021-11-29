import logging
from pkgutil import get_data

import requests
from typing import Dict
import json

import requests

logger = logging.getLogger('rtm.RaptoreumApi')


class RaptoreumApi:
    def __init__(self):
        self._base = "https://explorer.raptoreum.com/api"
        self.api = requests.Session()

    def get_data(self, endpoint: str, json_response=False):
        try:
            response = self.api.get(f"{self._base}/{endpoint}")
        except Exception as exc:
            logger.error(exc)
            raise Exception(exc)

        if json_response:
            try:
                return response.json()
            except json.decoder.JSONDecodeError as err:
                logger.error("RTM API ERROR endpoint: %s, content: %s\n error: %s", endpoint, response.content, err)
                return None

        return response

    def get_mining_info(self) -> Dict:
        """
        Get current network mining information
        :return:
        {
                "blocks": nnn, (numeric) The current block
                "currentblockweight": nnn, (numeric) The last block weight
                "currentblocktx": nnn, (numeric) The last block transaction
                "difficulty": xxx.xxxxx (numeric) The current difficulty
                "networkhashps": nnn, (numeric) The network hashes per second
                "hashespersec": nnn, (numeric) The hashes per second of built-in miner
                "pooledtx": n (numeric) The size of the mempool
                "chain": "xxxx", (string) current network name as defined in BIP70 (main, test, regtest)
                "warnings": "..." (string) any network and blockchain warnings
        }
        """
        return self.get_data('getmininginfo', json_response=True)

    def supply(self) -> float:
        """
        Get current supply
        :return: current coin supply as number
        """
        return self.get_data("supply", json_response=True)

    def marketcap(self) -> str:
        """
        Get current market cap
        :return: current coin market cap ฿ value / $ value. i.e ฿1/$4400
        """
        res = self.get_data('marketcap')
        return res.content.decode('utf-8')

    def smartnode(self, command: str) -> Dict:
        """
        Execute smartnode action base on given command
        Parameters:
            command - string: command for smartnode. Possible Commands: "count", "list", "current", "winner", and "winners"
        :return: current network smartnode information base on request params
        """
        commands_list = frozenset(["count", "list", "current", "winner", "winners"])
        if command not in commands_list:
            logger.error("Invalid command")
            return {}
        res = self.get_data(f'smartnode?command={command}', json_response=True)
        return res

    def gettotallockedcoins(self) -> str:
        """
        Get total coins that are locked by smartnode.
        :return: Total coin lock value and total lock % in following format. totalLockedValue/%
        """
        return self.get_data('gettotallockedcoins').content.decode('utf-8')
