from libs.py_eth_async.client import Client
from task.tenderly_actions import TenderlyActions
from libs.py_eth_async.data.models import Network
from data.tenderly_settings import access_key, user
from utils.networks import InitNetwork as init_network


class TenderlyClient:
    @staticmethod
    async def main(network: str):
        client = Client(
            private_key='',
            network=init_network.NETWORKS_MAP[network],
        )

        # Create Fork and Add ETH to Wallet on Tenderly
        tenderly = TenderlyActions(client=client)
        tenderly_fork_id = await tenderly.create_fork(access_key=access_key, user=user)
        await tenderly.add_assets_to_wallet(access_key=access_key, fork_id=tenderly_fork_id)

        # RPC and Client Data For Tenderly
        NETWORK_TENDERLY = Network(
            name='NETWORK_TENDERLY',
            rpc=f'https://rpc.tenderly.co/fork/{tenderly_fork_id}',
            chain_id=1,
            tx_type=2,
            coin_symbol='ANY',
        )

        client = Client(
            private_key='',
            network=NETWORK_TENDERLY,
        )

        return client, tenderly, tenderly_fork_id
