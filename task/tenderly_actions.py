import json
import os
import time

import requests
from loguru import logger

from libs.py_eth_async.data.models import TokenAmount
from task.farming_tenderly import Functions
from data.models import BaseContract
from utils.helper import DateTimeConverter


class TenderlyActions(Functions):
    async def create_fork(self, access_key: str, user: str) -> str:
        headers = {
            'authority': 'api.tenderly.co',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'nl',
            "X-Access-Key": f"{access_key}",
            'content-type': 'application/json',
            'origin': 'https://dashboard.tenderly.co',
            'referer': 'https://dashboard.tenderly.co/',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                          f'(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        }

        json_data = {
            'network_id': f'{self.client.network.chain_id}',
            'alias': '',
            'description': '',
            'chain_config': {
                'chain_id': int(self.client.network.chain_id),
            },
        }

        response = requests.post(
            f'https://api.tenderly.co/api/v1/account/{user}/project/project/fork',
            headers=headers,
            json=json_data,
        )

        response_json = response.json()
        fork_id = response_json["simulation_fork"]["id"]

        return fork_id

    async def add_assets_to_wallet(self, access_key: str, fork_id: str):
        headers = {
            'authority': 'rpc.tenderly.co',
            "X-Access-Key": f"{access_key}",
            'accept': '*/*',
            'accept-language': 'nl',
            'cache-control': 'max-age=0',
            'content-type': 'application/json',
            'origin': 'https://dashboard.tenderly.co',
            'referer': 'https://dashboard.tenderly.co/',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        }

        json_data = {
            'method': 'tenderly_addBalance',
            'params': [
                [
                    f'{self.client.account.address}', 
                ],
                '0x19E0C9BAB24000000000',  # 1000 ETH 0x3635c9adc5dea00000
            ],
            'id': 42,
            'jsonrpc': '2.0',
        }

        requests.post(f'https://rpc.tenderly.co/fork/{fork_id}',
                      headers=headers,
                      json=json_data)

    async def add_token_to_wallet(self, access_key: str, fork_id: str, token: BaseContract, amount: TokenAmount):

        headers = {
            'authority': 'rpc.tenderly.co',
            "X-Access-Key": f"{access_key}",
            'accept': '*/*',
            'accept-language': 'nl',
            'cache-control': 'max-age=0',
            'content-type': 'application/json',
            'origin': 'https://dashboard.tenderly.co',
            'referer': 'https://dashboard.tenderly.co/',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        }

        json_data = {
            'method': 'tenderly_setErc20Balance',
            'params': [
                f'{token.address}',
                [
                    f'{self.client.account.address}',
                ],
                f'{hex(amount.Wei)}',
            ],
            'id': 42,
            'jsonrpc': '2.0',
        }

        requests.post(f'https://rpc.tenderly.co/fork/{fork_id}',
                      headers=headers,
                      json=json_data)

    async def request_tx_simulation(self,
                                    contract: BaseContract,
                                    block_header: dict,
                                    tx_hex: str,
                                    block: int,
                                    gas: int,
                                    next_tx_id: str,
                                    access_key: str,
                                    user: str,
                                    tenderly_fork_id: str,
                                    value: str = '0',
                                    balance_cheker: bool = False,
                                    balance_of: bool = False,
                                    value_of: bool = False,
                                    wallet_address: str | None = None,
                                    farming_token: BaseContract | None = None,
                                    ) -> json:
        if block_header:
            logger.debug(f'{self.client.account.address} | Sending Simulation to Tenderly |'
                         f' Block: {int(block_header["number"], 16)},'
                         f' Time: {await DateTimeConverter.from_unix(int(block_header["timestamp"], 16))}')
        else:
            logger.debug(f'{self.client.account.address} | Sending Simulation to Tenderly |'
                         f' Block: {block},'
                         f' Time: {await DateTimeConverter.from_unix(int(time.time()))}')

        payload = {
            'network_id': f'{self.client.network.chain_id}',
            'block_number': None,
            'transaction_index': None,
            'from': f"{self.client.account.address}" if not wallet_address else wallet_address,
            'input': tx_hex,
            'to': f"{contract.address}",
            'gas': gas,
            'gas_price': '0',
            'value': value,
            'save': True,
            'source': 'dashboard',
            'block_header': None,
            'root': next_tx_id,
            'skip_fork_head_update': False,
            'alias': '',
            'description': '',
        }
        if block_header:
            payload["block_header"] = block_header

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Access-Key": f"{access_key}",

        }
        url = (f"https://api.tenderly.co/api/v1/account/{user}/project/project/fork/"
               f"{tenderly_fork_id}/simulate")
        response = requests.post(url, json=payload, headers=headers)

        json_response = response.json()
        tx_id = json_response["simulation"]["id"]
        directory = '/Users/alexgray/Desktop/Python/Web3/tenderly_simulations/files/'
        file_path = os.path.join(directory, 'tenderly_dict.json')
        with open(file_path, 'w') as file:
            json.dump(json_response, file, indent=4)

        if balance_cheker:
            try:
                if value_of:
                    for event in json_response['transaction']['transaction_info']['logs']:
                        if event['name'] == "Transfer":
                            for input_data in event['inputs']:
                                if input_data['soltype']['name'] == "wad":
                                    # Return the tx_id and "wad" value
                                    return tx_id, input_data['value']

                state_diff = json_response["transaction"]["transaction_info"]["state_diff"]
                for entry in state_diff:
                    if entry['address'] == farming_token.address.lower():
                        dirty_data = entry.get("dirty", {})
                        if "0xf00df46064689248bfafc885d0cfa35097ace45f" in dirty_data:
                            balance = dirty_data["0xf00df46064689248bfafc885d0cfa35097ace45f"]
                            return tx_id, balance
            except:
                with open(file_path, 'w') as file:
                    json.dump(json_response, file, indent=4)

                logger.error(f'Error, Can not find value of (balance_checker)')

                state_diff = json_response["transaction"]["transaction_info"]["state_diff"]
                transfer_value = None
                for log in json_response["transaction"]["transaction_info"]["logs"]:
                    if log["name"] == "Transfer":
                        for input_data in log["inputs"]:
                            if input_data["soltype"]["name"] == "value":
                                value = input_data["value"]
                                return tx_id, value

                harvested_value = None
                for entry in state_diff:
                    if entry['address'] == "0x1628d1d2cf4a9b64295c4b420ec346477fde430d":
                        dirty_data = entry.get("dirty", {})
                        if "0xf00df46064689248bfafc885d0cfa35097ace45f" in dirty_data:
                            value = dirty_data["0xf00df46064689248bfafc885d0cfa35097ace45f"]
                            return tx_id, value

                value = None
                for entry in state_diff:
                    if entry['address'] == "0x1628d1d2cf4a9b64295c4b420ec346477fde430d":
                        dirty_data = entry.get("dirty", {})
                        if "0xf00df46064689248bfafc885d0cfa35097ace45f" in dirty_data:
                            value = dirty_data["0xf00df46064689248bfafc885d0cfa35097ace45f"]
                            return tx_id, value

                value = json_response["transaction"]["transaction_info"]["call_trace"]["asset_changes"][0][
                    "raw_amount"]
                return tx_id, value

        if balance_of:
            balance = json_response["transaction"]["transaction_info"]["call_trace"]["decoded_output"][0]["value"]
            return tx_id, balance

        return tx_id

    async def request_root_branch(self, tx_id: str, root_name: str, access_key: str, user: str, fork_id: str):
        json_data = {
            'branch_root': True,
            'skip_fork_head_update': False,
            'alias': f'{root_name}',
            'description': '',
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Access-Key": f"{access_key}",

        }

        requests.put(
            f'https://api.tenderly.co/api/v1/account/{user}/project/project/fork/'
            f'{fork_id}/transaction/{tx_id}',
            headers=headers,
            json=json_data,
        )


    @staticmethod
    async def request_global_head(access_key: str, fork_id: str, user: str):
        headers = {
            'authority': 'api.tenderly.co',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'nl',
            "X-Access-Key": f"{access_key}",
            'origin': 'https://dashboard.tenderly.co',
            'referer': 'https://dashboard.tenderly.co/',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        }

        response = requests.get(
            f'https://api.tenderly.co/api/v1/account/{user}/project/project/fork/{fork_id}',
            headers=headers,
        )

        response_json = response.json()

        return response_json["simulation_fork"]["global_head"]
