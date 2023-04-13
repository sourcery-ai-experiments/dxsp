import os
import logging
from dotenv import load_dotenv
import json
import requests
import asyncio
from web3 import Web3
from pycoingecko import CoinGeckoAPI

from dxsp.assets.blockchains import blockchains

logging.getLogger(__name__).addHandler(logging.NullHandler())

class DexSwap:


    def __init__(self,
                 chain_id: int = 1, 
                 wallet_address: str = None,
                 private_key: str = None,
                 block_explorer_api: str = None,

                 block_explorer_url: str = None,
                 rpc: str = None,
                 w3: Web3 = None,
                 protocol_type: str = None,
                 dex_exchange: str = None,
                 base_trading_symbol: str = None,
                 amount_trading_option: int = 1,
                 ):
        self.chain_id = chain_id
        blockchain = blockchains[self.chain_id]

        self.wallet_address = wallet_address
        self.private_key = private_key
        self.block_explorer_api = block_explorer_api

        self.block_explorer_url = block_explorer_url
        if self.block_explorer_url is None:
            self.block_explorer_url = blockchain["block_explorer_url"]

        self.rpc = rpc
        if self.rpc is None:
            self.rpc = blockchain["rpc"]

        self.w3 = w3
        if self.w3 is None:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc))

        self.protocol_type = protocol_type
        if self.protocol_type is None:
            if self.protocol_type == "0x":
                base_url = blockchain["0x"]
            elif self.protocol_type == "1inch_limit":
                base_url = blockchain["1inch_limit"]
            else:
                base_url = blockchain["1inch"]
            self.dex_url = f"{base_url}"
        self.dex_exchange = dex_exchange
        if (
            self.dex_exchange is None
            or self.dex_exchange != blockchain["uniswap_v3"]
        ):
            self.router = blockchain["uniswap_v2"]
        else:
            self.router = blockchain["uniswap_v3"]
        self.base_trading_symbol = base_trading_symbol
        if self.base_trading_symbol is None:
            self.base_trading_symbol= 'USDC'

        self.amount_trading_option = amount_trading_option

        #🦎GECKO
        self.gecko_api = CoinGeckoAPI() # llama_api = f"https://api.llama.fi/" maybe as backup to be reviewed


    @staticmethod
    def _get(url, params=None, headers=None):
        headers = { "User-Agent": "Mozilla/5.0" }
        response = requests.get(url,params =params,headers=headers)
        return response.json()

    async def get_quote(self, symbol):
            asset_in_address = await self.search_contract(symbol)
            asset_out_address = await self.search_contract(self.base_trading_symbol)
            try:
                if self.protocol_type == "1inch":
                    asset_out_amount=1000000000000
                    quote_url = f"{self.dex_url}/quote?fromTokenAddress={asset_in_address}&toTokenAddress={asset_out_address}&amount={asset_out_amount}"
                    quote = self._get(quote_url)
                    return quote['toTokenAmount']
                if self.protocol_type in ["uniswap_v2","uniswap_v3"]:
                    return
            except Exception:
                return

    async def get_abi(self,addr):
        try:
            url = self.block_explorer_url
            params = {
                "module": "contract",
                "action": "getabi",
                "address": addr,
                "apikey": self.block_explorer_api }
            headers = { "User-Agent": "Mozilla/5.0" }
            resp = requests.get(url=url,params =params,headers=headers)
            response = resp.json() 
            abi = response["result"]
            return abi if (abi!="") else None
        except Exception:
            return

    async def get_approve(self, asset_out_address: str, amount=None):
        if self.protocol_type in ["1inch","1inch_limit"]:
            approval_check_URL = f"{self.dex_url}/approve/allowance?tokenAddress={asset_out_address}&walletAddress={self.wallet_address}"
            approval_response =  self._get(approval_check_URL)
            approval_check = approval_response['allowance']
            if (approval_check==0):
                approval_URL = f"{self.dex_url}/approve/transaction?tokenAddress={asset_out_address}"
                approval_response =  self._get(approval_URL)
        elif self.protocol_type in ["uniswap_v2","uniswap_v3"]:
            asset_out_abi= await self.get_abi(asset_out_address)
            asset_out_contract = self.w3.eth.contract(address=asset_out_address, abi=asset_out_abi)           
            approval_check = asset_out_contract.functions.allowance(self.w3.to_checksum_address(self.wallet_address), self.w3.to_checksum_address(self.router)).call()
            if (approval_check==0):
                approved_amount = (self.w3.to_wei(2**64-1,'ether'))
                asset_out_abi = await fetch_abi_dex(asset_out_address)
                asset_out_contract = self.w3.eth.contract(address=asset_out_address, abi=asset_out_abi)
                approval_TX = asset_out_contract.functions.approve(self.w3.to_checksum_address(self.router), approved_amount)
                approval_txHash = await sign_transaction_dex(approval_TX)
                approval_txHash_complete = self.w3.eth.wait_for_transaction_receipt(approval_txHash, timeout=120, poll_latency=0.1)

    async def get_sign(self, tx):
        try:
            if self.protocol_type in ['uniswap_v2']:
                tx_params = {
                'from': self.wallet_address,
                'gas': await self.get_gas(tx),
                'gasPrice': await self.get_gasPrice(tx),
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                }
                tx = tx.build_transaction(tx_params)
            elif self.protocol_type in ['uniswap_v3']:
                tx_params = {
                'from': self.wallet_address,
                'gas': await estimate_gas(tx),
                'gasPrice': self.w3.to_wei(gasPrice,'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
                }
                tx = tx.build_transaction(tx_params)
            elif self.protocol_type in ["1inch","1inch_limit"]:
                tx = tx['tx']
                tx['gas'] = await estimate_gas(tx)
                tx['nonce'] = self.w3.eth.get_transaction_count(self.wallet_address)
                tx['value'] = int(tx['value'])
                tx['gasPrice'] = int(ex.to_wei(gasPrice,'gwei'))
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            raw_tx = signed.rawTransaction
            return self.w3.eth.send_raw_transaction(raw_tx)
        except Exception:
            return

    async def get_gas(tx):
        gasestimate= self.web3.eth.estimate_gas(tx) * 1.25
        return int(self.w3.to_wei(gasestimate,'wei'))

    async def get_gasPrice(tx):
        gasprice= self.w3.eth.generate_gas_price()
        return self.w3.to_wei(gasPrice,'gwei')

    async def execute_order(self,direction,symbol,stoploss=10000,takeprofit=10000,quantity=1,amount_trading_option=1):

        try:
            asset_out_symbol = self.base_trading_symbol if direction=="BUY" else symbol
            asset_in_symbol = symbol if direction=="BUY" else self.base_trading_symbol
            asset_out_contract = await self.get_token_contract(asset_out_symbol)
            asset_out_decimals = asset_out_contract.functions.decimals().call()
            asset_out_balance = await self.get_token_balance(asset_out_symbol)
            if amount_trading_option == 1:
                asset_out_amount = ((asset_out_balance)/(10 ** asset_out_decimals))*(float(quantity)/100) #buy or sell %p percentage DEFAULT OPTION
            if amount_trading_option == 2:
                asset_out_amount = (asset_out_balance)/(10 ** asset_out_decimals) #SELL all token in case of sell order for example
      
            swap = self.get_swap(asset_out_symbol,asset_in_symbol,asset_out_amount)

        except Exception:
            return  

    async def get_swap(self, 
            asset_out_symbol: str, 
            asset_in_symbol: str,
            amount: int, 
            slippage_tolerance_percentage = 2 
        ):


        try:
            
            #ASSET OUT 
            asset_out_address = await self.search_contract(asset_out_symbol)
            asset_out_contract = await self.get_token_contract(asset_out_symbol)
            if asset_out_contract is None:
                return
            asset_out_decimals=asset_out_contract.functions.decimals().call()
            asset_out_balance = await self.get_token_balance(asset_out_symbol)
            if asset_out_balance == 0:
                return 
            #ASSETS IN 
            asset_in_address = await self.search_contract(asset_in_symbol)
            if asset_in_address is None:
                return

            #AMOUNT
            asset_out_decimals = asset_out_contract.functions.decimals().call()
            asset_out_amount = amount * 10 ** asset_out_decimals
            slippage = slippage_tolerance_percentage # defaulted to 2% slippage if not given
            asset_out_amount_converted = self.w3.to_wei(amount,'ether')

            transaction_amount = int((asset_out_amount_converted *(slippage/100)))

            #VERIFY IF ASSET OUT IS APPROVED
            await self.get_approve(asset_out_address)

            #1INCH
            if self.protocol_type in ["1inch"]:
                swap_url = f"{self.dex_url}/swap?fromTokenAddress={asset_out_address}&toTokenAddress={asset_in_address}&amount={transaction_amount}&fromAddress={self.wallet_address}&slippage={slippage}"
                swap_TX = self._get(swap_url)
                TX_status_code = swap_TX['statusCode']
                if TX_status_code != 200:
                    return
            #UNISWAP V2
            if self.protocol_type ['uniswap_v2']:
                order_path_dex=[asset_out_address, asset_in_address]
                router_abi = await self.get_abi(self.router)
                router_instance = self.w3.eth.contract(address=self.w3.to_checksum_address(self.router), abi=self.router_abi)
                deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
                transaction_min_amount  = int(router_instance.functions.getAmountsOut(transaction_amount, order_path_dex).call()[1])
                swap_TX = router_instance.functions.swapExactTokensForTokens(transaction_amount,transaction_min_amount,order_path_dex,self.wallet_address,deadline)
            #1INCH LIMIT
            if self.protocol_type ["1inch_limit"]:
                 return
                # encoded_message = encode_structured_data(eip712_data)
                # signed_message = await sign_transaction_dex(encoded_message)
                # # this is the limit order that will be broadcast to the limit order API
                # limit_order = {
                #     "orderHash": signed_message.messageHash.hex(),
                #     "signature": signed_message.signature.hex(),
                #     "data": order_data,
                # }
                # limit_order_url = dex_1inch_limit_api + str(chain_id) +"/limit-order" # make sure to change the chain_id if you are not using ETH mainnet
                # response = requests.post(url=limit_order_url,headers={"accept": "application/json, text/plain, */*", "content-type": "application/json"}, json=limit_order)

            #UNISWAP V3
            if self.protocol_type ['uniswap_v3']:
                return
            if swap_TX:
                signed_TX = await self.get_sign(swap_TX)
                txHash = str(self.w3.to_hex(signed_TX))
                txResult = await self.get_block_explorer_status(txHash)
                txHashDetail= self.w3.wait_for_transaction_receipt(txHash, timeout=120, poll_latency=0.1)
                if(txResult == "1"):
                    return txHash
        except Exception:
            return

    async def get_block_explorer_status (txHash):
        checkTransactionSuccessURL = f"{self.block_explorer_url}?module=transaction&action=gettxreceiptstatus&txhash={txHash}&apikey={self.block_explorer_api}"
        checkTransactionRequest =  self.get(checkTransactionSuccessURL)
        return checkTransactionRequest['status']

    async def search_gecko_contract(self,token):
        try:
            coin_info = await self.search_gecko(token)
            return coin_info['platforms'][f'{coin_platform}']
        except Exception:
            return

    async def search_gecko(self,token):
        try:
            search_results = self.gecko_api.search(query=token)
            search_dict = search_results['coins']
            filtered_dict = [x for x in search_dict if x['symbol'] == token.upper()]
            api_dict = [ sub['api_symbol'] for sub in filtered_dict ]
            for i in api_dict:
                coin_dict = self.gecko_api.get_coin_by_id(i)
                try:
                    coin_platform = await self.search_gecko_platform()
                    if coin_dict['platforms'][f'{coin_platform}'] is not None:
                        return coin_dict
                except KeyError:
                    pass
        except Exception:
            return

    async def search_gecko_platform(self):
        try:
            assetplatform = self.gecko_api.get_asset_platforms()
            output_dict = [x for x in assetplatform if x['chain_identifier'] == int(self.chain_id)]
            return output_dict[0]['id']
        except Exception:
            return

    async def get_contract_address(self,token_list_url, symbol):
        try: 
            token_list = self._get(token_list_url)
            token_search = token_list['tokens']
            for keyval in token_search:
                if (keyval['symbol'] == symbol and keyval['chainId'] == self.chain_id):
                    return keyval['address']
        except Exception:
            return

    async def search_contract(self, token):
        #📝tokenlist
        main_list = 'https://raw.githubusercontent.com/viaprotocol_type/tokenlists/main/all_tokens/all.json'
        personal_list = os.getenv("TOKEN_LIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/TT.json")
        test_token_list=os.getenv("TEST_TOKEN_LIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/testnet.json")

        try:
            token_contract = await self.get_contract_address(main_list,token)
            if token_contract is None:
                token_contract = await self.get_contract_address(test_token_list,token)
            if token_contract is None:
                token_contract = await self.get_contract_address(personal_list,token)
            if token_contract is None:
                token_contract = await self.search_gecko_contract(token)
            if len(token_contract)>1:
                return self.w3.to_checksum_address(token_contract)
        except Exception:
            return

    async def get_token_contract(self, token):
        try:
            token_address= await self.search_contract(token)
            token_abi= await self.get_abi(token_address)
            return self.w3.eth.contract(address=token_address, abi=token_abi)
        except Exception:
            return

    async def get_token_balance(self, token):
        try:
            token_contract = await self.get_token_contract(token)
            token_balance = token_contract.functions.balanceOf(self.wallet_address).call()
            return 0 if token_balance <=0 or token_balance is None else token_balance
        except Exception:
            return 0

