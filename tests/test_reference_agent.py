import asyncio

from superajan12.agents.reference import CryptoReferenceAgent


class FakeBinance:
    async def reference_snapshot(self, symbol: str):
        return {"source": "binance", "symbol": symbol, "mark_price": 100.0}


class FakeOKX:
    async def reference_snapshot(self, inst_id: str):
        return {"source": "okx", "symbol": inst_id, "last_price": 100.2}


class FakeCoinbase:
    async def reference_snapshot(self, product_id: str):
        return {"source": "coinbase", "symbol": product_id, "last_price": 99.9}


class BadCoinbase:
    async def reference_snapshot(self, product_id: str):
        return {"source": "coinbase", "symbol": product_id, "last_price": 120.0}


def test_reference_agent_accepts_close_prices() -> None:
    agent = CryptoReferenceAgent(
        binance=FakeBinance(),
        okx=FakeOKX(),
        coinbase=FakeCoinbase(),
        max_deviation_bps=75,
    )

    result = asyncio.run(agent.check_btc())

    assert result.ok is True
    assert result.median_price == 100.0
    assert result.max_deviation_bps is not None


def test_reference_agent_rejects_large_deviation() -> None:
    agent = CryptoReferenceAgent(
        binance=FakeBinance(),
        okx=FakeOKX(),
        coinbase=BadCoinbase(),
        max_deviation_bps=75,
    )

    result = asyncio.run(agent.check_btc())

    assert result.ok is False
    assert any("deviation" in reason for reason in result.reasons)
