# 100 Ajan Programı

Not: Bu çalışma ortamı aynı anda 100 ajan çalıştırmıyor. Bu yüzden program 100 bağımsız ajan rolü olarak tasarlandı ve dalgalar halinde yürütülecek.

## Yönetim Kuralı

- Aynı anda küçük bir dalga çalışır.
- Her ajan dar sahiplik alanına sahiptir.
- Her dalga sonunda bulgular birleşik mimariye ve koda işlenir.
- Hiçbir ajan tek başına “para kazandıran” iddia üretmez; bütün öneriler doğrulama, risk ve canlıya geçiş kapısından geçer.

## Dalga 1: Venue ve Yürütme Temeli

1. Binance futures venue capability araştırması
2. Binance order lifecycle adapter tasarımı
3. Binance market data sequencing tasarımı
4. Deribit testnet/prod fark analizi
5. Deribit JSON-RPC execution adapter tasarımı
6. Deribit rate-limit ve OTV guard araştırması
7. Coinbase Advanced Trade preview/order akışı
8. Coinbase portfolio segregation modeli
9. OKX policy/KYC gating araştırması
10. OKX demo vs live trading capability haritası

## Dalga 2: Risk Motoru ve Güvenlik Kafesi

11. Global kill switch stratejisi
12. Venue-specific kill switch stratejisi
13. Stale-data lock tasarımı
14. Duplicate intent/idempotency stratejisi
15. Max position ve inventory clamp
16. Max leverage ve liquidation-distance guard
17. Funding-rate exposure guard
18. Max drawdown intraday lock
19. Cross-venue correlation exposure guard
20. Order-rate ve cancel-rate throttling

## Dalga 3: Piyasa Verisi ve Durum Doğruluğu

21. Unified book snapshot şeması
22. Incremental diff reconciliation
23. Heartbeat ve liveness modeli
24. Sequence-gap recovery akışı
25. Checksum abstraction modeli
26. Trade tape normalizasyonu
27. Funding ve mark-price beslemesi
28. Liquidation ve OI veri katmanı
29. Market regime feature store
30. Multi-venue clock skew ölçümü

## Dalga 4: Alpha Araştırma Çerçevesi

31. Trend-following research lane
32. Mean-reversion research lane
33. Basis/funding research lane
34. Liquidation-flow research lane
35. Order-book imbalance research lane
36. Volatility breakout research lane
37. Event-driven news research lane
38. Social sentiment research lane
39. On-chain flow research lane
40. Regime-switching meta-model research lane

## Dalga 5: Araştırma Altyapısı

41. Historical replay engine
42. Feature extraction pipeline
43. Labeling framework
44. Walk-forward validation runner
45. Slippage model araştırması
46. Fill-quality metric paketi
47. PnL explained ratio analizi
48. Overfitting dedektörü
49. Experiment registry
50. Research report template generator

## Dalga 6: Advisory AI Katmanı

51. News summarizer agent
52. On-chain anomaly agent
53. Social volatility agent
54. Macro regime summarizer
55. Confidence calibration agent
56. Contradiction detector
57. Narrative drift detector
58. Prompt schema hardening agent
59. Advisory-to-deterministic interface verifier
60. Shadow-mode AI evaluator

## Dalga 7: Portföy ve Sermaye Yönetimi

61. Capital allocator
62. Per-strategy risk budgeter
63. Venue cash segmentation
64. Margin buffer planner
65. Loss-recovery cooldown policy
66. Position netting policy
67. Inventory skew controller
68. Portfolio health dashboard logic
69. Canary capital ladder
70. Emergency de-risk playbook

## Dalga 8: Dayanıklılık ve Operasyon

71. Restart recovery agent
72. Event replay recovery agent
73. Storage durability hardening
74. Chaos scenario author
75. Fault injection runner
76. SLO ve error budget tanımı
77. Alert rule builder
78. Incident timeline exporter
79. Postmortem template agent
80. Runbook author

## Dalga 9: Uyum ve Politika

81. Venue changelog watcher
82. API agreement watcher
83. KYC requirement tracker
84. Jurisdiction routing policy
85. Audit trail completeness checker
86. Operator action logging policy
87. Secrets and credential segmentation
88. Access control design
89. Retention and evidence export
90. Managed-account boundary analysis

## Dalga 10: Ürün ve Son Birleştirme

91. Dashboard information architecture
92. Execution timeline UX
93. Research observability UX
94. Risk cockpit UX
95. Strategy comparison surface
96. Deployment packaging
97. Environment matrix author
98. End-to-end scenario runner
99. Release readiness reviewer
100. Final integration and merge captain

## Birleştirme Kuralı

- Her dalga sonunda yalnızca doğrulanmış kararlar ana koda girer.
- Alpha hipotezleri önce replay, sonra paper, sonra testnet, sonra canary canlı sermaye aşamasına geçer.
- “Para kazandırıyor” ifadesi ancak istatistiksel ve operasyonel doğrulama sonrası, net tarihli test sonuçlarıyla desteklenirse kullanılabilir.
