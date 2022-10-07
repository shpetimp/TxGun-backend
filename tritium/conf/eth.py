from web3 import Web3, HTTPProvider

ETHSCAN_TOKEN=
ETHSCAN_URL=

WEI_FROM_ETH = WEI = WEI_PER_ETH = 10**18
ETH_FROM_WEI = ETH = 1.0/WEI

GET_WEB3 = lambda host: Web3(HTTPProvider(host))

WEB3_INFURA = {'main': ,
               'ropsten': }

WEB3_DRIVERS = {k: GET_WEB3(v) for k, v in WEB3_INFURA.items()}

