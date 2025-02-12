"""
 DEXSWAP Unit Test
"""

from unittest.mock import AsyncMock

import pytest

from dxsp import DexSwap
from dxsp.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="dxsp")

@pytest.fixture(name="dex")
def DexSwap_fixture():
    return DexSwap()


@pytest.fixture(name="dex_client")
def client_fixture(dex):
    for dx in dex.clients:
        if dx.name == "eth":
            return dx


@pytest.fixture(name="dex_client_zero_x")
def client_zero_x_fixture(dex):
    for dx in dex.clients:
        if dx.protocol == "zerox":
            return dx


@pytest.fixture(name="order")
def order_params_fixture():
    """Return order parameters."""
    return {
        "action": "BUY",
        "instrument": "BTC",
        "quantity": 1,
    }


@pytest.fixture(name="invalid_symbol")
def invalid_symbol_fixture():
    """Return order parameters."""
    return {
        "action": "BUY",
        "instrument": "NOTATHING",
        "quantity": 1,
    }


# @pytest.fixture(name="invalid_order")
# def invalid_order_fixture():
#     """Return order parameters."""
#     return "not an order"


def test_dynaconf_is_in_testing():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing"


@pytest.mark.asyncio
async def test_dextrader(dex):
    """Init Testing"""
    assert isinstance(dex, DexSwap)
    assert dex.clients is not None
    assert callable(dex.get_info)
    assert callable(dex.get_balances)
    assert callable(dex.get_positions)
    assert callable(dex.get_pnl)
    assert callable(dex.submit_order)

    for dx in dex.clients:
        assert dx is not None
        assert dx.name is not None
        assert dx.protocol in ["uniswap", "zerox", "kwenta"]
        assert callable(dx.get_order_amount)
        assert callable(dx.replace_instrument)
        assert callable(dx.get_quote)
        assert callable(dx.get_swap)
        assert callable(dx.make_swap)
        assert callable(dx.get_account_balance)
        assert callable(dx.get_trading_asset_balance)
        assert callable(dx.get_account_margin)
        assert callable(dx.get_account_position)
        assert callable(dx.get_account_open_positions)
        assert callable(dx.get_account_pnl)
        if dx.protocol == "zerox":
            assert dx.api_key is not None
            assert dx.api_endpoint is not None


@pytest.mark.asyncio
async def test_get_info(dex):
    result = await dex.get_info()
    assert result is not None
    print(result)
    assert "ℹ️" in result
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_balances(dex):
    get_account_balance = AsyncMock()
    result = await dex.get_balances()
    assert result is not None
    assert "🏦" in result
    assert get_account_balance.awaited
    assert ("1" in result) or ("56" in result) or ("137" in result)


@pytest.mark.asyncio
async def test_get_positions(dex):
    get_account_position = AsyncMock()
    result = await dex.get_positions()
    assert result is not None
    assert "📊" in result
    assert "Opened" in result
    assert "Margin" in result
    assert get_account_position.awaited
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_pnls(dex):
    get_account_pnl = AsyncMock()
    result = await dex.get_pnl()
    assert result is not None
    assert "🏆" in result
    assert get_account_pnl.awaited
    assert ("1" in result) or ("56" in result)


@pytest.mark.asyncio
async def test_get_quotes(dex):
    """getquote Testing"""
    get_quote = AsyncMock()
    result = await dex.get_quotes(symbol="WBTC")
    assert result is not None
    assert "⚖️" in result
    assert get_quote.awaited
    assert ("eth" in result) or ("pol" in result)
    numerical_count = len([char for char in result if char.isdigit()])
    assert numerical_count >= 9


@pytest.mark.asyncio
async def test_get_quotes_invalid(dex):
    """getquote Testing"""
    result = await dex.get_quotes(symbol="NOTATOKEN")
    assert "⚖️" in result
    assert "None" in result


@pytest.mark.asyncio
async def test_submit_order(dex, order):
    result = await dex.submit_order(order)
    assert result is not None


@pytest.mark.asyncio
async def test_submit_invalid_symbol(dex, invalid_symbol):
    result = await dex.submit_order(invalid_symbol)
    assert result is not None
    assert "⚠️" in result


# @pytest.mark.asyncio
# async def test_submit_order_invalid(dex, invalid_order):
#     result = await dex.submit_order(invalid_order)
#     assert "⚠️" in result


@pytest.mark.asyncio
async def test_get_quote_zero_x(dex_client_zero_x):

    result = await dex_client_zero_x.get_quote(
        buy_address="0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",  # USDT
        sell_address="0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",  # WBTC
        amount=1,
    )
    assert result is not None
    assert result > 0
