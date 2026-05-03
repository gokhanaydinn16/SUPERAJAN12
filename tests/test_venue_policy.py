from __future__ import annotations

import unittest

from src.agent_os.venue_policy import REGISTRY, find_policy


class VenuePolicyTests(unittest.TestCase):
    def test_registry_contains_known_venues(self) -> None:
        names = {policy.name for policy in REGISTRY}
        self.assertIn("Binance USDT Futures", names)
        self.assertIn("Deribit", names)
        self.assertIn("Coinbase Advanced Trade", names)
        self.assertIn("OKX", names)

    def test_find_policy_returns_none_for_unknown(self) -> None:
        self.assertIsNone(find_policy("Nonexistent Venue"))

    def test_find_policy_returns_match(self) -> None:
        policy = find_policy("OKX")
        self.assertIsNotNone(policy)
        self.assertTrue(policy.supports_demo)
        self.assertIn("KYC Level 2", policy.live_kyc_requirement)
        self.assertTrue(policy.policy_sensitive)


if __name__ == "__main__":
    unittest.main()
