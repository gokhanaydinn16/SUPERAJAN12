from __future__ import annotations

from superajan12.models import Decision, Market, OrderBookSnapshot, RiskDecision
from superajan12.risk_controls import PreTradeVeto, PreTradeVetoCode, RiskControlContext, veto_reason


class RiskEngine:
    """Conservative first-pass risk engine.

    The risk engine is the boss of the system. Strategy modules can suggest an
    idea, but this class decides whether the system may even create a paper-trade
    idea. Live execution will require stricter checks later.
    """

    def __init__(
        self,
        max_market_risk_usdc: float,
        max_daily_loss_usdc: float,
        min_volume_usdc: float,
        max_spread_bps: float,
        min_liquidity_usdc: float,
    ) -> None:
        self.max_market_risk_usdc = max_market_risk_usdc
        self.max_daily_loss_usdc = max_daily_loss_usdc
        self.min_volume_usdc = min_volume_usdc
        self.max_spread_bps = max_spread_bps
        self.min_liquidity_usdc = min_liquidity_usdc

    def evaluate_market(
        self,
        market: Market,
        order_book: OrderBookSnapshot | None,
        current_daily_pnl_usdc: float = 0.0,
        safe_mode: bool = False,
        reference_gate_ok: bool | None = None,
        reference_gate_reasons: list[str] | None = None,
        control_context: RiskControlContext | None = None,
    ) -> RiskDecision:
        context = control_context or RiskControlContext(
            current_daily_pnl_usdc=current_daily_pnl_usdc,
            safe_mode=safe_mode,
        )
        reasons: list[str] = []
        vetoes: list[PreTradeVeto] = []

        if context.safe_mode:
            vetoes.append(PreTradeVeto(PreTradeVetoCode.SAFE_MODE, "safe-mode aktif; yeni islem yok"))

        if context.kill_switch_active:
            vetoes.append(PreTradeVeto(PreTradeVetoCode.KILL_SWITCH, "kill-switch aktif; yeni islem yok"))

        if not context.connected:
            vetoes.append(PreTradeVeto(PreTradeVetoCode.DISCONNECTED, "baglanti yok; yeni islem yok"))

        if context.market_data_stale:
            vetoes.append(PreTradeVeto(PreTradeVetoCode.STALE_DATA, "piyasa verisi stale; yeni islem yok"))

        if context.current_daily_pnl_usdc <= -abs(self.max_daily_loss_usdc):
            vetoes.append(PreTradeVeto(PreTradeVetoCode.DAILY_LOSS_LIMIT, "gunluk zarar limiti dolmus"))

        requested_risk = context.requested_risk_usdc
        if requested_risk is None:
            requested_risk = self.max_market_risk_usdc

        if context.max_market_exposure_usdc is not None:
            projected_market_exposure = context.current_market_exposure_usdc + max(requested_risk, 0.0)
            if projected_market_exposure > context.max_market_exposure_usdc:
                vetoes.append(
                    PreTradeVeto(
                        PreTradeVetoCode.POSITION_CAP,
                        (
                            "market exposure cap asilacak: "
                            f"{projected_market_exposure:.2f} > {context.max_market_exposure_usdc:.2f} USDC"
                        ),
                    )
                )

        if context.max_total_exposure_usdc is not None:
            projected_total_exposure = context.current_total_exposure_usdc + max(requested_risk, 0.0)
            if projected_total_exposure > context.max_total_exposure_usdc:
                vetoes.append(
                    PreTradeVeto(
                        PreTradeVetoCode.EXPOSURE_CAP,
                        (
                            "toplam exposure cap asilacak: "
                            f"{projected_total_exposure:.2f} > {context.max_total_exposure_usdc:.2f} USDC"
                        ),
                    )
                )

        if market.closed or not market.active:
            vetoes.append(PreTradeVeto(PreTradeVetoCode.MARKET_INACTIVE, "market aktif degil"))

        if market.volume_usdc < self.min_volume_usdc:
            vetoes.append(
                PreTradeVeto(
                    PreTradeVetoCode.LOW_VOLUME,
                    f"hacim dusuk: {market.volume_usdc:.2f} < {self.min_volume_usdc:.2f} USDC",
                )
            )

        if market.liquidity_usdc < self.min_liquidity_usdc:
            vetoes.append(
                PreTradeVeto(
                    PreTradeVetoCode.LOW_LIQUIDITY,
                    f"likidite dusuk: {market.liquidity_usdc:.2f} < {self.min_liquidity_usdc:.2f} USDC",
                )
            )

        if order_book is None:
            vetoes.append(PreTradeVeto(PreTradeVetoCode.ORDERBOOK_UNAVAILABLE, "orderbook okunamadi"))
        else:
            if order_book.best_bid is None or order_book.best_ask is None:
                vetoes.append(PreTradeVeto(PreTradeVetoCode.ORDERBOOK_INCOMPLETE, "orderbook eksik"))
            elif order_book.spread_bps is None:
                vetoes.append(PreTradeVeto(PreTradeVetoCode.SPREAD_UNAVAILABLE, "spread hesaplanamadi"))
            elif order_book.spread_bps > self.max_spread_bps:
                vetoes.append(
                    PreTradeVeto(
                        PreTradeVetoCode.SPREAD_TOO_WIDE,
                        f"spread genis: {order_book.spread_bps:.1f} bps > {self.max_spread_bps:.1f} bps",
                    )
                )

        if reference_gate_ok is False:
            vetoes.append(PreTradeVeto(PreTradeVetoCode.REFERENCE_GATE, "referans fiyat kapisi reddetti"))
            if reference_gate_reasons:
                reasons.extend(reference_gate_reasons)

        vetoes.extend(context.extra_vetoes)
        reasons = [veto_reason(veto.code, veto.reason) for veto in vetoes] + reasons

        if reasons:
            return RiskDecision(decision=Decision.REJECT, max_risk_usdc=0.0, reasons=reasons)

        return RiskDecision(
            decision=Decision.APPROVE,
            max_risk_usdc=self.max_market_risk_usdc,
            reasons=["risk kontrolleri gecti"],
        )
