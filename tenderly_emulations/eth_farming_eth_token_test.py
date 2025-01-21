import time
import asyncio
from loguru import logger
from decimal import Decimal

from utils.helper import Helper
from data.models import Contract
from data.tenderly_settings import access_key, user, gas, day
from task.farming_tenderly import Functions
from task.tenderly_actions import TenderlyActions
from libs.py_eth_async.data.models import TokenAmount
from tenderly_emulations.init_client import TenderlyClient


async def main():
    client, tenderly, tenderly_fork_id = await TenderlyClient.main(network='ethereum')

    tenderly = TenderlyActions(client=client)
    farming_simulation = Functions(client=client)
    eth_price = Decimal(await Helper.get_token_price('ETH'))

    # Tenderly Data
    block_header = {}
    now = int(time.time())
    block = await client.w3.eth.block_number

    # Contracts
    pool = 1
    contract_token_a = Contract.TOKEN_A
    contract_lp_token = Contract.TOKEN_LP
    farming_contract = Contract.Farming_Ethereum
    contract_token_farming = Contract.TOKEN_FARMING

    uniswap_contract = Contract.UniswapV2Router02

    # Actions
    # ========= Swap ETH to Token ========= #
    amount = TokenAmount(amount=0.000960911)
    tx_hex = await farming_simulation.swapExactETHForTokens(amount=amount,
                                                            contract_token=contract_token_a)
    global_head = await tenderly.request_global_head(user=user,
                                                     access_key=access_key,
                                                     fork_id=tenderly_fork_id,
                                                     )
    tx_id = await tenderly.request_tx_simulation(contract=uniswap_contract, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=global_head,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id,
                                                 value=str(amount.Wei))
    root_name = 'Swap ETH to Token'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    # ========= Approve Token ========= #
    tx_hex = await farming_simulation.approve_token(contract_token=contract_token_a, spender=uniswap_contract)

    tx_id = await tenderly.request_tx_simulation(contract=contract_token_a, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    root_name = 'Approve Token For Uniswap'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    # ========= Create LP ========= #
    tx_hex = await farming_simulation.addLiquidityETH(token_a=contract_token_a, eth_amount=amount)
    tx_id = await tenderly.request_tx_simulation(contract=uniswap_contract, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id,
                                                 value=str(amount.Wei))
    root_name = 'Create LP Token/ETH'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    # ========= Approve LP ========= #
    tx_hex = await farming_simulation.approve_token(contract_token=contract_lp_token, spender=farming_contract)
    tx_id = await tenderly.request_tx_simulation(contract=contract_lp_token, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    root_name = 'Approve LP For Farming'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    # ========= Deposit to Farming ========= #
    tx_hex = await farming_simulation.deposit_token_to_farming(contract_lp_token=contract_lp_token,
                                                               farm_contract=farming_contract, pool=pool)
    tx_id = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id, )
    root_name = 'Deposit LP to Farming'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    # Claim After 7 days
    next_time = now + day * 7
    next_block = block + (7150 * 7)
    block_header = {
        "number": hex(next_block),
        "timestamp": hex(next_time),
    }
    tx_hex = await farming_simulation.withdraw(farm_contract=farming_contract, pool=pool)
    _, balance = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                      tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                      access_key=access_key, user=user,
                                                      tenderly_fork_id=tenderly_fork_id,
                                                      balance_cheker=True)

    balance = TokenAmount(amount=int(balance), wei=True)
    logger.warning(f'Token Balance After 7 days: {balance.Ether}')

    # Claim After 14 days
    next_time = now + day * 14
    next_block = block + (7150 * 14)
    block_header = {
        "number": hex(next_block),
        "timestamp": hex(next_time),
    }
    tx_hex = await farming_simulation.withdraw(farm_contract=farming_contract, pool=pool)
    _, balance = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                      tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                      access_key=access_key, user=user,
                                                      tenderly_fork_id=tenderly_fork_id, balance_cheker=True)

    balance = TokenAmount(amount=int(balance), wei=True)
    logger.warning(f'Token Balance After 14 days: {balance.Ether}')

    # Claim After 21 days
    next_time = now + day * 21
    next_block = block + (7150 * 21)
    block_header = {
        "number": hex(next_block),
        "timestamp": hex(next_time),
    }
    tx_hex = await farming_simulation.withdraw(farm_contract=farming_contract, pool=pool)
    _, balance = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                      tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                      access_key=access_key, user=user,
                                                      tenderly_fork_id=tenderly_fork_id,
                                                      balance_cheker=True)

    balance = TokenAmount(amount=int(balance), wei=True)
    logger.warning(f'Token Balance After 21 days: {balance.Ether}')

    # Claim After 30 days
    next_time = now + day * 30
    next_block = block + (7150 * 30)
    block_header = {
        "number": hex(next_block),
        "timestamp": hex(next_time),
    }
    tx_hex = await farming_simulation.withdraw(farm_contract=farming_contract, pool=pool)
    _, balance = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                      tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                      access_key=access_key, user=user,
                                                      tenderly_fork_id=tenderly_fork_id,
                                                      balance_cheker=True)
    balance = TokenAmount(amount=int(balance), wei=True)
    logger.warning(f'Token Balance After 30 days: {balance.Ether}')

    # Claim After 60 days
    next_time = now + day * 180
    next_block = block + (7150 * 180)
    block_header = {
        "number": hex(next_block),
        "timestamp": hex(next_time),
    }
    tx_hex = await farming_simulation.withdraw(farm_contract=farming_contract, pool=pool)
    tx_id, balance = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
                                                          tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                          access_key=access_key, user=user,
                                                          tenderly_fork_id=tenderly_fork_id,
                                                          balance_cheker=True)
    root_name = 'Withdraw from Farming - 60 days'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    balance = TokenAmount(amount=int(balance), wei=True)
    logger.warning(f'Token Balance After 60 days: {balance.Ether}')

    # Check Balance
    tx_hex = ""
    _, balance = await tenderly.request_tx_simulation(contract=contract_token_farming, block_header=block_header,
                                                      tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                      access_key=access_key, user=user,
                                                      tenderly_fork_id=tenderly_fork_id,
                                                      balance_of=True)
    balance = TokenAmount(amount=int(balance), wei=True)

    # ========= Approve Token ========= #
    tx_hex = await farming_simulation.approve_token(contract_token=contract_token_farming, spender=uniswap_contract)

    tx_id = await tenderly.request_tx_simulation(contract=contract_token_farming, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    root_name = 'Approve Token For Uniswap'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)

    # Sell Tokens
    block_header = {
        "number": hex(next_block),
        "timestamp": hex(next_time),
    }
    tx_hex = await farming_simulation.swapExactTokensForETH(contract_token=contract_token_farming, timestamp=next_time)
    tx_id = await tenderly.request_tx_simulation(contract=uniswap_contract, block_header=block_header,
                                                 tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
                                                 access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    root_name = 'Sell Tokens - 60 days'
    await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
                                       access_key=access_key, user=user, fork_id=tenderly_fork_id)
    #
    # # Withdraw LP from Farming
    # tx_hex = await farming_simulation.emergencyWithdraw(farming_contract=farming_contract, pool=pool)
    # tx_id = await tenderly.request_tx_simulation(contract=farming_contract, block_header=block_header,
    #                                              tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
    #                                              access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    # root_name = 'Withdraw LP from Farming'
    # await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
    #                                    access_key=access_key, user=user, fork_id=tenderly_fork_id)
    #
    # # Check Balance of LP Token
    # tx_hex = ""
    # _, balance = await tenderly.request_tx_simulation(contract=contract_lp_token, block_header=block_header,
    #                                                   tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
    #                                                   access_key=access_key, user=user,
    #                                                   tenderly_fork_id=tenderly_fork_id,
    #                                                   balance_of=True)
    # balance = TokenAmount(amount=int(balance), wei=True)
    # logger.warning(f'LP Token Balance After Withdraw from Farming: {balance.Ether}')
    #
    # # ========= Approve LP Token ========= #
    # tx_hex = await farming_simulation.approve_token(contract_token=contract_lp_token, spender=uniswap_contract)
    #
    # tx_id = await tenderly.request_tx_simulation(contract=contract_lp_token, block_header=block_header,
    #                                              tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
    #                                              access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    # root_name = 'Approve LP Token'
    # await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
    #                                    access_key=access_key, user=user, fork_id=tenderly_fork_id)
    #
    # # Remove of LP Token Liquidity
    # tx_hex = await farming_simulation.removeLiquidityETH(contract_token_a=contract_token_a,
    #                                                      lp_balance=balance, time_stamp=next_time)
    # tx_id = await tenderly.request_tx_simulation(contract=uniswap_contract, block_header=block_header,
    #                                              tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
    #                                              access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    # root_name = 'Withdraw LP from Farming'
    # await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
    #                                    access_key=access_key, user=user, fork_id=tenderly_fork_id)
    #
    # # ========= Approve Token ========= #
    # tx_hex = await farming_simulation.approve_token(contract_token=contract_token_a, spender=uniswap_contract)
    #
    # tx_id = await tenderly.request_tx_simulation(contract=contract_token_a, block_header=block_header,
    #                                              tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
    #                                              access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    # root_name = 'Approve Token A'
    # await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
    #                                    access_key=access_key, user=user, fork_id=tenderly_fork_id)
    #
    # # Sell Tokens
    # tx_hex = await farming_simulation.swapExactTokensForETH(contract_token=contract_token_a, timestamp=next_time)
    # tx_id = await tenderly.request_tx_simulation(contract=uniswap_contract, block_header=block_header,
    #                                              tx_hex=tx_hex, block=block, gas=gas, next_tx_id=tx_id,
    #                                              access_key=access_key, user=user, tenderly_fork_id=tenderly_fork_id)
    # root_name = 'Sell Tokens Token A'
    # await tenderly.request_root_branch(tx_id=tx_id, root_name=root_name,
    #                                    access_key=access_key, user=user, fork_id=tenderly_fork_id)


asyncio.run(main())
