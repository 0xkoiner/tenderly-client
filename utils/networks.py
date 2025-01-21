from libs.py_eth_async.data.models import Network


class InitNetwork:
    ETH = Network(
        name='ETH_TENDERLY',
        rpc='https://ethereum-rpc.publicnode.com',
        chain_id=1,
        tx_type=2,
        coin_symbol='ETH',
    )
    BSC = Network(
        name='BSC_TENDERLY',
        rpc='https://polygon-mainnet.public.blastapi.io',
        chain_id=56,
        tx_type=1,
        coin_symbol='BNB',
    )
    POLYGON = Network(
        name='POLYGON_TENDERLY',
        rpc='https://polygon-mainnet.public.blastapi.io',
        chain_id=137,
        tx_type=2,
        coin_symbol='POL',
    )
    AVALANCHE = Network(
        name='AVAX_TENDERLY',
        rpc='https://polygon-mainnet.public.blastapi.io',
        chain_id=43114,
        tx_type=2,
        coin_symbol='AVAX',
    )
    MOONRIVER = Network(
        name='MOONRIVER_TENDERLY',
        rpc='https://polygon-mainnet.public.blastapi.io',
        chain_id=1285,
        tx_type=2,
        coin_symbol='AVAX',
    )
    BASE = Network(
        name='BASE_TENDERLY',
        rpc='https://polygon-mainnet.public.blastapi.io',
        chain_id=8453,
        tx_type=2,
        coin_symbol='ETH',
    )
    ARBITRUM = Network(
        name='ARBITRUM_TENDERLY',
        rpc='https://polygon-mainnet.public.blastapi.io',
        chain_id=42161,
        tx_type=2,
        coin_symbol='ETH',
    )
    NETWORKS_MAP = {
        'ethereum': ETH,
        'bsc': BSC,
        'polygon': POLYGON,
        'avalanche': AVALANCHE,
        'moonriver': MOONRIVER,
        'base': BASE,
        'arbitrum': ARBITRUM,
    }
