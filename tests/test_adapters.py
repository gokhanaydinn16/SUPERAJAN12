from __future__ import annotations

import unittest

from src.agent_os.adapters import (
    BinanceFuturesAdapter,
    CoinbaseAdvancedTradeAdapter,
    DeribitAdapter,
    OKXAdapter,
    get_adapter,
)
from src.agent_os.domain import OrderIntent, OrderSide, OrderType


class AdapterTests(unittest.TestCase):
    def _intent(self) -> OrderIntent:
        return OrderIntent("BTC-PERP", "binance-futures", OrderSide.BUY, 0.5, OrderType.LIMIT, price=100_000)

    def test_deribit_submission(self) -> None:
        adapter = DeribitAdapter()
        response = adapter.submit_order(self._intent())
        self.assertEqual(response.venue, "Deribit")
        self.assertIn("queued", response.status)

    def test_binance_submission(self) -> None:
        adapter = BinanceFuturesAdapter()
        response = adapter.submit_order(self._intent())
        self.assertEqual(response.venue, "Binance USDT Futures")
        self.assertEqual(response.details["use_checksum"], "true")

    def test_coinbase_preview_and_submit(self) -> None:
        adapter = CoinbaseAdvancedTradeAdapter()
        preview = adapter.preview_order(self._intent())
        self.assertEqual(preview["preview_status"], "ready")
        response = adapter.submit_order(self._intent())
        self.assertEqual(response.details["preview_ok"], "true")

    def test_okx_submission(self) -> None:
        adapter = OKXAdapter()
        response = adapter.submit_order(self._intent())
        self.assertEqual(response.details["policy_sensitive"], "true")

    def test_registry_lookup(self) -> None:
        adapter = get_adapter("Deribit")
        self.assertEqual(adapter.venue_name, "Deribit")


if __name__ == "__main__":
    unittest.main()
