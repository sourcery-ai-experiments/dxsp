import json
import requests
import asyncio
from web3 import Web3
import many_abis as ma

class DexSwap:

    chain_id =
                {
          "1": "ethereum",
          "10": "optimism",
          "56": "binance",
          "137": "polygon",
          "250": "fantom",
          "42161": "arbitrum",
          "42220": "celo",
          "43114": "avalanche"
        }
    execution_mode =
           {
          "1": "1inch",
          "2": "1inch_limit",
          "3": "Uniswap_v2",
          "4": "Uniswap_v3",
          "5": "0x",
          "6": "0x_limit"
        }

    def __init__(self,
                 web3: Web3 = None,
                 chain_id, 
                 wallet_address,
                 private_key,
                 execution_mode=1,
                 dex_exchange):
        self.chain_id = chain_id
        self.address = wallet_address
        self.private_key = private_key
        self.execution_mode = execution_mode
        self.dex_exchange = dex_exchange

        if execution_mode == 1
            base_url = 'https://api.1inch.exchange/'
            version = "v5.0"
        url = f"{base_url}/{version}/{chainId}"

    @staticmethod
    def _get(url, params=None, headers=None):
        headers = { "User-Agent": "Mozilla/5.0" }
        response = requests.get(url,params =params,headers=headers)
        return response.json()
    def swap(self, from_token_symbol: str, to_token_symbol: str,
                 amount: float, slippage=None, decimal=None, send_address=None):
        #await #approve_asset_router(asset_out_address,asset_out_contract)
        swap_url = f"{url}/swap?fromTokenAddress={asset_out_address}&toTokenAddress={asset_in_address}&amount={transaction_amount}&fromAddress={walletaddress}&slippage={slippage}"
        #swap_TX = await retrieve_url_json(swap_url)
        #tx_token= await sign_transaction_dex(swap_TX)
        #return tx_token
    def get_approve(self, from_token_symbol: str, amount=None, decimal=None):
        return
        # approval_check_URL = f"{dex_1inch_api}/{chainId}/approve/allowance?tokenAddress={asset_out_address}&walletAddress={walletaddress}"
        # approval_response = await retrieve_url_json(approval_check_URL)
        # approval_check = approval_response['allowance']
        # if (approval_check==0):
        #     approval_URL = f"{dex_1inch_api}/{chainId}/approve/transaction?tokenAddress={asset_out_address}"
        #     approval_response = await retrieve_url_json(approval_URL)
    #def get_sign()
        # try:
        #     if dex_version in ['uni_v2']:
        #         tx_params = {
        #         'from': walletaddress,
        #         'gas': int(gasLimit),
        #         'gasPrice': ex.to_wei(gasPrice,'gwei'),
        #         'nonce': ex.eth.get_transaction_count(walletaddress),
        #         }
        #         tx = tx.build_transaction(tx_params)
        #     if dex_version in ['uni_v3']:
        #         tx_params = {
        #         'from': walletaddress,
        #         'gas': await estimate_gas(tx),
        #         'gasPrice': ex.to_wei(gasPrice,'gwei'),
        #         'nonce': ex.eth.get_transaction_count(walletaddress),
        #         }
        #         tx = tx.build_transaction(tx_params)
        #     elif dex_version == "1inch_v5":
        #         tx = tx['tx']
        #         tx['to'] = ex.to_checksum_address(tx['to'])
        #         tx['gas'] = await estimate_gas(tx)
        #         tx['nonce'] = ex.eth.get_transaction_count(walletaddress)
        #         tx['value'] = int(tx['value'])
        #         tx['gasPrice'] = int(ex.to_wei(gasPrice,'gwei'))
        #     signed = ex.eth.account.sign_transaction(tx, privatekey)
        #     raw_tx = signed.rawTransaction
        #     return ex.eth.send_raw_transaction(raw_tx)
        # except Exception as e:
        #     logger.debug(msg=f"sign_transaction_dex contract {tx} error {e}")
        #     await handle_exception(e)
        #     return
    def get_quote()
        return
    def get_token()
        return
    def get_abi()
        return

    # async def search_json_contract(symbol):
    #     try:
    #         alltokenlist=os.getenv("TOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/TT.json") #https://raw.githubusercontent.com/viaprotocol/tokenlists/main/all_tokens/all.json
    #         token_list = await retrieve_url_json(alltokenlist)
    #         logger.info(msg=f"token_list {token_list}")
    #         token_search = token_list['tokens']
    #         for keyval in token_search:
    #             if (keyval['symbol'] == symbol and keyval['chainId'] == int(chainId)):
    #                 logger.info(msg=f"address {keyval['address']}")
    #                 return keyval['address']
    #     except Exception as e:
    #         logger.error(msg=f"search_json_contract error {symbol} {e}")

# class DexLimitSwap:
    # dex_1inch_limit_api = "https://limit-orders.1inch.io/v3.0"
    # dex_0x_api = "https://api.0x.org/orderbook/v1"

if __name__ == '__main__':
    pass