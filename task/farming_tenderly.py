import time
from typing import Any
from loguru import logger

from libs.py_eth_async.client import Client
from data.models import Contract, BaseContract
from libs.py_eth_async.data.models import TokenAmount, TxArgs


class Functions:
    def __init__(self, client: Client):
        self.client = client

    async def token_balance_checker(self, contract_token: BaseContract) -> TokenAmount:
        token_balance = await self.client.wallet.balance(token=contract_token.address)
        logger.success(f'{self.client.account.address} Balance of Token: {token_balance.Ether}')
        return token_balance

    async def swapExactETHForTokens(self,
                                    *,
                                    timestamp: int = 0,
                                    amount: TokenAmount,
                                    contract_token: BaseContract,
                                    weth: BaseContract = Contract.WETH,
                                    wallet_address: str | None = None,
                                    middle_token: BaseContract | None = None,
                                    router: BaseContract = Contract.UniswapV2Router02) -> str:
        await self.balance_checker()
        logger.debug(f'{self.client.account.address} Starting Swap to Token | Amount: {amount.Ether} ETH')
        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            amountOut=0,
            path=[weth.address, contract_token.address] if not middle_token else
            [weth.address, middle_token.address, contract_token.address],
            to=self.client.account.address if not wallet_address else wallet_address,
            deadline=int(time.time() + 600) if not timestamp else timestamp + 600,
        )

        swap_data = contract.encodeABI('swapExactETHForTokens', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
            'value': amount.Wei,
        }

        return tx_params['data']

    async def swapExactAVAXForTokens(self,
                                     *,
                                     timestamp: int = 0,
                                     amount: TokenAmount,
                                     contract_token: BaseContract,
                                     weth: BaseContract = Contract.WAVAX,
                                     middle_token: BaseContract | None = None,
                                     router: BaseContract = Contract.UniswapV2Router02) -> str:
        await self.balance_checker()
        logger.debug(f'{self.client.account.address} Starting Swap to Token | Amount: {amount.Ether} ETH')
        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            _amountOutMin=0,
            _pairBinSteps=[0],
            _tokenPath=[weth.address, contract_token.address] if not middle_token else
            [weth.address, middle_token.address, contract_token.address],
            _to=self.client.account.address,
            _deadline=int(time.time() + 600) if not timestamp else timestamp + 600,
        )

        swap_data = contract.encodeABI('swapExactAVAXForTokens', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
            'value': amount.Wei,
        }

        return tx_params['data']

    async def swapExactTokensForAVAX(self,
                                     *,
                                     timestamp: int = 0,
                                     contract_token: BaseContract,
                                     weth: BaseContract = Contract.WAVAX,
                                     middle_token: BaseContract | None = None,
                                     router: BaseContract = Contract.UniswapV2Router02) -> str:
        await self.balance_checker()
        logger.debug(f'{self.client.account.address} Starting Sell Tokens to Avax')
        balance = await self.client.wallet.balance(token=contract_token.address)
        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            amountIn=balance.Wei,
            amountOutMin=0,
            path=[contract_token.address, weth.address] if not middle_token else
            [contract_token.address, middle_token.address, weth.address],
            to=self.client.account.address,
            deadline=int(time.time() + 600) if not timestamp else timestamp + 600,
        )

        swap_data = contract.encodeABI('swapExactTokensForAVAX', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def swapExactTokensForTokens(self,
                                       *,
                                       timestamp: int = 0,
                                       half: bool = False,
                                       contract_token_a: BaseContract,
                                       contract_token_b: BaseContract,
                                       router: BaseContract = Contract.UniswapV2Router02) -> str:
        await self.balance_checker()
        logger.debug(f'{self.client.account.address} Starting Swap to Token to Token')
        token_balance = await self.client.wallet.balance(token=contract_token_a)
        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            amountIn=token_balance.Wei if not half else int(token_balance.Wei / 2),
            amountOutMin=0,
            path=[contract_token_a.address, contract_token_b.address],
            to=self.client.account.address,
            deadline=int(time.time() + 600) if not timestamp else timestamp + 600,
        )

        swap_data = contract.encodeABI('swapExactTokensForTokens', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def swapExactTokensForTokensSupportingFeeOnTransferTokens(self,
                                                                    *,
                                                                    timestamp: int = 0,
                                                                    half: bool = False,
                                                                    contract_token_a: BaseContract,
                                                                    contract_token_b: BaseContract,
                                                                    router: BaseContract = Contract.UniswapV2Router02) \
            -> str:
        await self.balance_checker()
        logger.debug(f'{self.client.account.address} Starting Swap to Token to Token')
        token_balance = await self.client.wallet.balance(token=contract_token_a)
        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            amountIn=token_balance.Wei if not half else int(token_balance.Wei / 2),
            amountOutMin=0,
            path=[contract_token_a.address, contract_token_b.address],
            to=self.client.account.address,
            deadline=int(time.time() + 600) if not timestamp else timestamp + 600,
        )

        swap_data = contract.encodeABI('swapExactTokensForTokensSupportingFeeOnTransferTokens', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def approve_token(self,
                            contract_token: BaseContract,
                            spender: BaseContract, ) -> str:
        logger.debug(f'{self.client.account.address} Approving Token | '
                     f'Token: {contract_token.address}, Spender: {spender.address}')
        token_amount = TokenAmount(
            amount=115792089237316195423570985008687907853269984665640564039457584007913129639935,
            wei=True)

        contract = await self.client.contracts.get(contract_address=contract_token)

        tx_args = TxArgs(
            _spender=spender.address,
            _value=token_amount.Wei,
        )
        swap_data = contract.encodeABI('approve', args=tx_args.tuple())
        nonce = await self.client.wallet.nonce()
        tx_params = {
            'chainId': self.client.network.chain_id,
            'nonce': nonce,
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data
        }

        return tx_params['data']

    async def addLiquidity(self,
                           token_a: BaseContract,
                           token_b: BaseContract,
                           router: BaseContract = Contract.UniswapV2Router02) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit LP to {router.title}')

        contract = await self.client.contracts.get(contract_address=router)
        token_a_balance = await self.token_balance_checker(contract_token=token_a)
        token_b_balance = await self.token_balance_checker(contract_token=token_b)

        tx_args = TxArgs(
            tokenA=token_a.address,
            tokenB=token_b.address,
            amountADesired=token_a_balance.Wei,
            amountBDesired=token_b_balance.Wei,
            amountAMin=0,
            amountBMin=0,
            to=self.client.account.address,
            deadline=int(time.time() + 600),
        )

        swap_data = contract.encodeABI('addLiquidity', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def addLiquidity_with_pair(self,
                                     token_a: BaseContract,
                                     token_b: BaseContract,
                                     lp_token: BaseContract,
                                     router: BaseContract = Contract.UniswapV2Router02) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit LP to {router.title}')

        contract = await self.client.contracts.get(contract_address=router)
        token_a_balance = await self.token_balance_checker(contract_token=token_a)
        token_b_balance = await self.token_balance_checker(contract_token=token_b)

        tx_args = TxArgs(
            pair=lp_token.address,
            tokenA=token_a.address,
            tokenB=token_b.address,
            amountADesired=token_a_balance.Wei,
            amountBDesired=token_b_balance.Wei,
            amountAMin=0,
            amountBMin=0,
            to=self.client.account.address,
            deadline=int(time.time() + 600),
        )

        swap_data = contract.encodeABI('addLiquidity', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def addLiquidityAvax(self,
                               token_a: BaseContract,
                               token_b: BaseContract,
                               router: BaseContract = Contract.UniswapV2Router02) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit LP to {router.title}')

        contract = await self.client.contracts.get(contract_address=router)
        token_a_balance = await self.token_balance_checker(contract_token=token_a)
        token_b_balance = await self.token_balance_checker(contract_token=token_b)

        tx_args = TxArgs(
            tokenA=token_a.address,
            tokenB=token_b.address,
            amountADesired=token_a_balance.Wei,
            amountBDesired=token_b_balance.Wei,
            amountAMin=0,
            amountBMin=0,
            to=self.client.account.address,
            deadline=int(time.time() + 600),
            buybackRoutes=[[token_a.address, token_b.address], [token_b.address]],
        )

        swap_data = contract.encodeABI('addLiquidity', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def addLiquidityWithAvax(self,
                                   token_a: BaseContract,
                                   router: BaseContract = Contract.UniswapV2Router02) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit LP to {router.title}')

        contract = await self.client.contracts.get(contract_address=router)
        token_a_balance = await self.token_balance_checker(contract_token=token_a)

        tx_args = TxArgs(
            token=token_a.address,
            amountTokenDesired=token_a_balance.Wei,
            amountTokenMin=0,
            amountAVAXMin=0,
            to=self.client.account.address,
            deadline=int(time.time() + 600),
        )

        swap_data = contract.encodeABI('addLiquidityAVAX', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def addLiquidityETH(self,
                              *,
                              token_a: BaseContract,
                              eth_amount: TokenAmount,
                              router: BaseContract = Contract.UniswapV2Router02,
                              ) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit LP to {router.title}')
        contract = await self.client.contracts.get(contract_address=router)
        token_a_balance = await self.token_balance_checker(contract_token=token_a)

        tx_args = TxArgs(
            token=token_a.address,
            amountTokenDesired=token_a_balance.Wei,
            amountTokenMin=0,
            amountETHMin=0,
            to=self.client.account.address,
            deadline=int(time.time() + 600),
        )

        swap_data = contract.encodeABI('addLiquidityETH', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
            'value': eth_amount.Wei,
        }

        return tx_params['data']

    async def deposit_token_to_staking(self,
                                       contract_token: BaseContract,
                                       farm_contract: BaseContract) -> dict[str, Any] | bool:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Staking')
        token_balance = await self.token_balance_checker(contract_token=contract_token)

        contract = await self.client.contracts.get(contract_address=farm_contract)

        tx_args = TxArgs(
            amount=token_balance.Wei,
        )

        swap_data = contract.encodeABI('deposit', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }
        return tx_params['data']

    async def deposit_token_to_staking_with_timelock(self,
                                                     time_lock: int,
                                                     contract_token: BaseContract,
                                                     farm_contract: BaseContract,
                                                     wallet_address: str | None = None,
                                                     ) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Staking')
        if not wallet_address:
            token_balance = await self.token_balance_checker(contract_token=contract_token)
        else:
            address = self.client.w3.to_checksum_address(wallet_address)
            token_balance = await self.client.wallet.balance(token=contract_token.address, address=address)
        contract = await self.client.contracts.get(contract_address=farm_contract)

        tx_args = TxArgs(
            _amount=token_balance.Wei,
            _days=time_lock,
        )

        swap_data = contract.encodeABI('stake', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }
        return tx_params['data']

    async def deposit_token_to_staking_uni(self,
                                           *,
                                           pool: int | None = None,
                                           contract_token: BaseContract,
                                           farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Staking')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        token_balance = await self.token_balance_checker(contract_token=contract_token)

        tx_args = TxArgs(
            _term=pool,
            _amount=token_balance.Wei,

        )

        swap_data = contract.encodeABI('startLock', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def deposit_token_to_miner(self,
                                     amount: TokenAmount,
                                     miner_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Miner')
        contract = await self.client.contracts.get(contract_address=miner_contract)

        swap_data = '0x6b9808a1'

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
            'value': amount.Wei,
        }

        return tx_params['data']

    async def hatch_with_value(self,
                               value_of: int,
                               miner_contract: BaseContract) -> dict[str, Any] | bool:
        logger.debug(f'{self.client.account.address} | Starting Hatch to Miner')
        contract = await self.client.contracts.get(contract_address=miner_contract)

        tx_args = TxArgs(
            _amount=value_of,
        )

        swap_data = contract.encodeABI('consumeWine', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }
        return tx_params['data']

    async def deposit_token_to_staking_avax(self,
                                            contract_token: BaseContract,
                                            farm_contract: BaseContract) -> dict[str, Any] | bool:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Staking')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        token_balance = await self.token_balance_checker(contract_token=contract_token)

        tx_args = TxArgs(
            _amount=token_balance.Wei,
        )

        swap_data = contract.encodeABI('enter', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }
        return tx_params['data']

    async def deposit_token_to_staking_with_pool(self,
                                                 pool: int,
                                                 contract_token: BaseContract,
                                                 farm_contract: BaseContract) -> dict[str, Any] | bool:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Staking')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        token_balance = await self.token_balance_checker(contract_token=contract_token)

        tx_args = TxArgs(
            _pid=pool,
            _amount=token_balance.Wei,
        )

        swap_data = contract.encodeABI('deposit', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }
        return tx_params['data']

    async def deposit_token_to_staking_with_tokenId(self,
                                                    pool: int,
                                                    contract_token: BaseContract,
                                                    farm_contract: BaseContract) -> dict[str, Any] | bool:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Staking')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        token_balance = await self.token_balance_checker(contract_token=contract_token)

        tx_args = TxArgs(
            caveId=token_balance.Wei,
            tokenId=pool,
        )

        swap_data = contract.encodeABI('stake', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }
        return tx_params['data']

    async def deposit_token_to_farming(self,
                                       pool: int,
                                       contract_lp_token: BaseContract,
                                       farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        lp_token_balance = await self.token_balance_checker(contract_token=contract_lp_token)

        tx_args = TxArgs(
            _pid=pool,
            _amount=lp_token_balance.Wei,
        )
        swap_data = contract.encodeABI('deposit', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def deposit_token_to_farming_uni(self,
                                           *,
                                           pool: int,
                                           withdraw: bool = False,
                                           contract_lp_token: BaseContract,
                                           farm_contract: BaseContract,
                                           ) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        lp_token_balance = await self.token_balance_checker(contract_token=contract_lp_token)
        salesman = self.client.w3.to_checksum_address('0x0000000000000000000000000000000000000000')

        tx_args = TxArgs(
            pid=pool,
            amount=lp_token_balance.Wei if not withdraw else 0,
            to=self.client.account.address
        )

        swap_data = contract.encodeABI('deposit', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def deposit_token_to_staking_amount(self,
                                              contract_token_a: BaseContract,
                                              farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        lp_token_balance = await self.token_balance_checker(contract_token=contract_token_a)

        tx_args = TxArgs(
            pglAmount=lp_token_balance.Wei,
        )

        swap_data = contract.encodeABI('stake', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def deposit_token_to_staking_amount_uni(self,
                                                  contract_token_a: BaseContract,
                                                  farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} | Starting Deposit Token to Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        lp_token_balance = await self.token_balance_checker(contract_token=contract_token_a)

        tx_args = TxArgs(
            amount=lp_token_balance.Wei,
        )

        swap_data = contract.encodeABI('stake', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def withdraw(self, pool: int,
                       farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} Starting Withdraw from Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)

        tx_args = TxArgs(
            _pid=pool,
            _amount=0,
        )

        swap_data = contract.encodeABI('withdraw', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def increaseLockAmount(self,
                                 farm_contract: BaseContract,
                                 balance: TokenAmount) -> str:
        logger.debug(f'{self.client.account.address} Starting Withdraw from Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)

        tx_args = TxArgs(
            _amount=balance.Wei,
        )

        swap_data = contract.encodeABI('increaseLockAmount', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def claimReward(self,
                          farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} Starting Withdraw from Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)

        swap_data = contract.encodeABI('claimReward')

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def harvest(self,
                      farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} Starting Withdraw from Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)

        swap_data = contract.encodeABI('harvestToken')

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def withdraw_without_pool(self,
                                    amount: int,
                                    farm_contract: BaseContract,
                                    ) -> str:
        logger.debug(f'{self.client.account.address} Starting Withdraw from Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)

        tx_args = TxArgs(
            _amount=amount,
        )

        swap_data = contract.encodeABI('withdraw', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def get_reward(self,
                         farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} Starting Withdraw from Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)

        swap_data = '0x3d18b912'

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def compound(self,
                       miner_contract: BaseContract, ) -> str:
        logger.debug(f'{self.client.account.address} Starting Compound Miner')
        contract = await self.client.contracts.get(contract_address=miner_contract)

        swap_data = '0x9daf8f4b0000000000000000000000000000000000000000000000000000000000000001'

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def sell(self,
                   miner_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} Starting Sell Miner')
        contract = await self.client.contracts.get(contract_address=miner_contract)

        swap_data = '0x5f8d5123'

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def get_reward_with_pool(self,
                                   pool: int,
                                   farm_contract: BaseContract,
                                   ) -> str:
        logger.debug(f'{self.client.account.address} Starting Claim from Staking')

        contract = await self.client.contracts.get(contract_address=farm_contract)

        tx_args = TxArgs(
            _pid=pool,
        )

        swap_data = contract.encodeABI('getReward', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def claim_staking_fast(self,
                                 amount: TokenAmount,
                                 staking_contract: BaseContract,
                                 ) -> str:
        logger.debug(f'{self.client.account.address} Starting Claim from Staking')
        contract = await self.client.contracts.get(contract_address=staking_contract)

        tx_args = TxArgs(
            amount=amount.Wei,
        )

        swap_data = contract.encodeABI('withdrawRewardTokens', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def claim(self,
                    amount: TokenAmount,
                    staking_contract: BaseContract,
                    ) -> str:
        logger.debug(f'{self.client.account.address} Starting Claim from Staking')
        contract = await self.client.contracts.get(contract_address=staking_contract)

        tx_args = TxArgs(
            amount=amount.Wei,
        )

        swap_data = contract.encodeABI('withdrawRewardTokens', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def stake(self,
                    farm_contract: BaseContract,
                    contract_token: BaseContract,
                    ) -> str:
        logger.debug(f'{self.client.account.address} Starting Stake from Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        token_balance = await self.token_balance_checker(contract_token=contract_token)

        tx_args = TxArgs(
            amount=token_balance.Wei,
        )

        swap_data = contract.encodeABI('stake', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
            'value': 0
        }

        return tx_params['data']

    async def unstake(self,
                      farm_contract: BaseContract) -> str:
        logger.debug(f'{self.client.account.address} Starting Unstake from Farming')
        contract = await self.client.contracts.get(contract_address=farm_contract)

        tx_args = TxArgs(
            _amount=0,
        )

        swap_data = contract.encodeABI('unstake', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def leave(self,
                    farm_contract: BaseContract,
                    contract_token_farming: BaseContract,
                    ) -> str:
        logger.debug(f'{self.client.account.address} Starting Unstake from Staking')
        contract = await self.client.contracts.get(contract_address=farm_contract)
        token_balance = await self.client.wallet.balance(token=contract_token_farming.address)

        tx_args = TxArgs(
            _share=token_balance.Wei,
        )

        swap_data = contract.encodeABI('leave', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def swapExactTokensForETH(self,
                                    *,
                                    timestamp: int = 0,
                                    contract_token: BaseContract,
                                    weth: BaseContract = Contract.WETH,
                                    router: BaseContract = Contract.UniswapV2Router02) -> str:
        logger.debug(f'{self.client.account.address} Starting Sell Tokens to ETH')
        contract = await self.client.contracts.get(contract_address=router)
        token_balance = await self.token_balance_checker(contract_token=contract_token)

        tx_args = TxArgs(
            amountIn=token_balance.Wei,
            amountOutMin=0,
            path=[contract_token.address, weth.address],
            to=self.client.account.address,
            deadline=int(time.time() + 600) if not timestamp else timestamp + 600,
        )

        swap_data = contract.encodeABI('swapExactTokensForETH', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def swapExactTokensForETHSupportingFeeOnTransferTokens(self,
                                                                 *,
                                                                 timestamp: int = 0,
                                                                 contract_token: BaseContract,
                                                                 wallet_address: str | None = None,
                                                                 weth: BaseContract = Contract.WETH,
                                                                 router: BaseContract = Contract.UniswapV2Router02) -> str:
        logger.debug(f'{self.client.account.address} Starting Sell Tokens to ETH')

        if not wallet_address:
            token_balance = await self.token_balance_checker(contract_token=contract_token)
        else:
            address = self.client.w3.to_checksum_address(wallet_address)
            token_balance = await self.client.wallet.balance(token=contract_token.address, address=address)

        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            amountIn=token_balance.Wei,
            amountOutMin=0,
            path=[contract_token.address, weth.address],
            to=self.client.account.address if not wallet_address else wallet_address,
            deadline=int(time.time() + 600) if not timestamp else timestamp + 600,
        )

        swap_data = contract.encodeABI('swapExactTokensForETHSupportingFeeOnTransferTokens', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def balance_checker(self):
        native_balance = await self.client.wallet.balance()
        logger.success(f'{self.client.account.address} ETH Balance: {native_balance.Ether} ETH')

    async def emergencyWithdraw(self,
                                pool: int,
                                farming_contract: BaseContract,
                                ) -> str:
        logger.debug(f'{self.client.account.address} Starting Withdraw LP from Farming')
        contract = await self.client.contracts.get(contract_address=farming_contract)

        tx_args = TxArgs(
            _pid=pool,
        )

        swap_data = contract.encodeABI('emergencyWithdraw', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def removeLiquidityETH(self,
                                 time_stamp: int,
                                 lp_balance: TokenAmount,
                                 contract_token_a: BaseContract,
                                 router: BaseContract = Contract.UniswapV2Router02,
                                 ) -> str:
        logger.debug(f'{self.client.account.address} Starting Remove LP via Uniswap')

        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            token=contract_token_a.address,
            liquidity=lp_balance.Wei,
            amountTokenMin=0,
            amountETHMin=0,
            to=self.client.account.address,
            deadline=time_stamp + 600,
        )

        swap_data = contract.encodeABI('removeLiquidityETH', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def removeLiquidityAVAX(self,
                                  time_stamp: int,
                                  lp_balance: TokenAmount,
                                  contract_token_a: BaseContract,
                                  router: BaseContract = Contract.UniswapV2Router02,
                                  ) -> str:
        logger.debug(f'{self.client.account.address} Starting Remove LP via Uniswap')

        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            token=contract_token_a.address,
            liquidity=lp_balance.Wei,
            amountTokenMin=0,
            amountAVAXMin=0,
            to=self.client.account.address,
            deadline=time_stamp + 600,
        )

        swap_data = contract.encodeABI('removeLiquidityAVAX', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']

    async def removeLiquidity(self,
                              time_stamp: int,
                              lp_balance: TokenAmount,
                              contract_token_a: BaseContract,
                              contract_token_b: BaseContract,
                              router: BaseContract = Contract.UniswapV2Router02,
                              ) -> str:
        logger.debug(f'{self.client.account.address} Starting Remove LP via Uniswap')
        contract = await self.client.contracts.get(contract_address=router)

        tx_args = TxArgs(
            tokenA=contract_token_a.address,
            tokenB=contract_token_b.address,
            liquidity=lp_balance.Wei,
            amountAMin=0,
            amountBMin=0,
            to=self.client.account.address,
            deadline=time_stamp + 600,
        )

        swap_data = contract.encodeABI('removeLiquidity', args=tx_args.tuple())

        tx_params = {
            'from': self.client.account.address,
            'to': contract.address,
            'data': swap_data,
        }

        return tx_params['data']
