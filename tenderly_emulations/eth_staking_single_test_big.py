import time
import asyncio
from loguru import logger
from decimal import Decimal

from utils.helper import Helper
from data.models import Contract
from data.tenderly_settings import access_key, user, gas, day
from libs.py_eth_async.client import Client
from task.farming_tenderly import Functions
from task.tenderly_actions import TenderlyActions
from libs.py_eth_async.data.models import Network, TokenAmount


async def main():
    # RPC and Client Data
    ETH = Network(
        name='ETH_TENDERLY',
        rpc='https://rpc.ankr.com/eth',
        chain_id=1,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://etherscan.io/',
    )

    client = Client(
        private_key='',
        network=ETH,
    )

    # Create Fork and Add ETH to Wallet on Tenderly
    tenderly = TenderlyActions(client=client)
    tenderly_fork_id = await tenderly.create_fork(access_key=access_key, user=user)
    await tenderly.add_assets_to_wallet(access_key=access_key, fork_id=tenderly_fork_id)

    # RPC and Client Data For Tenderly
    ETH = Network(
        name='ETH_TENDERLY',
        rpc=f'https://rpc.tenderly.co/fork/{tenderly_fork_id}',
        chain_id=1,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://etherscan.io/',
    )

    client = Client(
        private_key='',
        network=ETH,
    )

    tenderly = TenderlyActions(client=client)
    farming_simulation = Functions(client=client)
    eth_price = Decimal(await Helper.get_token_price('ETH'))

    # Tenderly Data
    block = await client.w3.eth.block_number
    now = int(time.time())
    block_header = {}

    # Contracts
    contract_token_farming = Contract.TOKEN_FARMING
    contract_token_a = Contract.TOKEN_A
    farming_contract = Contract.Staking_TimeLock_Ethereum
    time_lock = 11  # Todo minimum 11 days
    uniswap_contract = Contract.UniswapV2Router02

    # Actions
    # ========= Swap ETH to Token A ========= #
    amount = TokenAmount(amount=1.90959)
    tx_hex = await farming_simulation.swapExactETHForTokens(amount=amount, contract_token=contract_token_a)
    global_head = await tenderly.request_global_head(access_key=access_key, fork_id=tenderly_fork_id, user=user)
    tx_id = await tenderly.request_tx_simulation(contract=uniswap_contract, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=global_head,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id,
                                                 value=str(amount.Wei))
    root_name = 'Swap ETH to Token'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    # ========= Approve Token A ========= #
    tx_hex = await farming_simulation.approve_token(contract_token=contract_token_a, spender=farming_contract)

    tx_id = await tenderly.request_tx_simulation(contract=contract_token_a, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    root_name = 'Approve Token A For Farming'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    # ========= Deposit to Farming ========= #
    tx_hex = await farming_simulation.deposit_token_to_staking_with_timelock(time_lock=time_lock,
                                                                             contract_token=contract_token_a,
                                                                             farm_contract=farming_contract)
    tx_id = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    root_name = 'Deposit Token to Farming'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    time_lock += 1
    # Claim After Time Lock Days
    for _ in range(32):
        next_time = now + day * time_lock
        next_block = block + (7150 * time_lock)
        block_header = {
            "number": hex(next_block),
            "timestamp": hex(next_time),
        }
        tx_hex = '0x4e71d92d'
        tx_id, balance = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                              tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                              access_key=access_key, user=user,
                                                              tenderly_fork_id=tenderly_fork_id,
                                                              balance_cheker=True)

        root_name = f'Withdraw from Farming - {time_lock} days'
        await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                           access_key=access_key, user=user, fork_id=tenderly_fork_id)

        balance = TokenAmount(amount=int(balance), wei=True)
        logger.warning(f'Token Balance After {time_lock} days: {balance.Ether}')

        tx_hex = await farming_simulation.deposit_token_to_staking_with_timelock(time_lock=11,
                                                                                 contract_token=contract_token_a,
                                                                                 farm_contract=farming_contract)
        tx_id = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                     tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                     access_key=access_key, user=user,
                                                     tenderly_fork_id=tenderly_fork_id)
        root_name = f'Deposit Token to Farming Day {time_lock}'
        await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                           access_key=access_key, user=user, fork_id=tenderly_fork_id)

        time_lock += 12

    # ========= Claim ========= #
    next_time = now + day * time_lock
    next_block = block + (7150 * time_lock)
    block_header = {
        "number": hex(next_block),
        "timestamp": hex(next_time),
    }
    tx_hex = '0x4e71d92d'
    tx_id, balance = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                          tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                          access_key=access_key, user=user,
                                                          tenderly_fork_id=tenderly_fork_id,
                                                          balance_cheker=True)

    root_name = f'Withdraw from Farming - {time_lock} days'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    balance = TokenAmount(amount=int(balance), wei=True)
    logger.warning(f'Token Balance After {time_lock} days: {balance.Ether}')

    # ========= Approve Token ========= #
    tx_hex = await farming_simulation.approve_token(contract_token=contract_token_farming, spender=uniswap_contract)

    tx_id = await tenderly.request_tx_simulation(contract=contract_token_farming, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    root_name = 'Approve Token For Uniswap'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    tx_hex = await farming_simulation.swapExactTokensForETHSupportingFeeOnTransferTokens(
        contract_token=contract_token_farming,
        timestamp=next_time)
    tx_id = await tenderly.request_tx_simulation(contract=uniswap_contract, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    root_name = f'Sell Tokens - {time_lock} days'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)


asyncio.run(main())
