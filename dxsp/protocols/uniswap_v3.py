"""
uniswap V3  🦄
"""

from dxsp.config import settings


@classmethod
async def get_quote_uniswap_v3(
    cls,
    asset_in_address,
    asset_out_address,
    amount=1
):
    pass
    # cls.logger.debug("get_quote_uniswap")
    # try:
    #     quoter = await self.quoter()
    #     sqrtPriceLimitX96 = 0
    #     fee = 3000
    #     quote = quoter.functions.quoteExactInputSingle(
    #         asset_in_address,
    #         asset_out_address,
    #         fee, amount, sqrtPriceLimitX96).call()
    #     return f"🦄 {quote} {settings.trading_asset}"
    # except Exception as e:
    #     return e

async def get_approve_uniswap_v3(self, token_address):
    pass


async def get_swap_uniswap_v3(self, asset_out_address, asset_in_address, amount):
    pass