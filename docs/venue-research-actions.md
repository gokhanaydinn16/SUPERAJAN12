# Venue Research -> Repo Actions

Tarih: 3 Mayıs 2026

Amaç, venue araştırmasını doğrudan repo işlerine çevirmek.

## Öncelik Sırası

1. Deribit
2. Binance USD-M Futures
3. Coinbase Advanced Trade
4. OKX

## Deribit

- Neden şimdi: Testnet canlıya yakın ve JSON-RPC modeli execution çekirdeğine iyi oturuyor.
- Ana risk: Testnet bakım kesintileri ve prod HFT farkı.
- Repo işi:
  1. Deribit order mapper
  2. Deribit market-data adapter
  3. Credit-based rate-limit guard

## Binance

- Neden şimdi: Yüksek likidite ve güçlü veri akışı.
- Ana risk: Diff-depth desync ve sıra boşluğu.
- Repo işi:
  1. Diff-depth replay ve gap recovery
  2. Desync metriği
  3. Order-rate throttle sertleştirmesi

## Coinbase Advanced Trade

- Neden şimdi: Order preview akışı deterministik pre-trade doğrulamayı güçlendirir.
- Ana risk: Sandbox sonucu canlı kaliteyi bire bir temsil etmeyebilir.
- Repo işi:
  1. `preview_order()` arayüzü
  2. Preview-pass ratio metriği
  3. Portfolio segregation desteği

## OKX

- Neden şimdi değil ama erken tasarım gerektiriyor: Policy ve KYC gating mimariyi etkiliyor.
- Ana risk: Canlı API kullanımı politika değişikliklerine duyarlı.
- Repo işi:
  1. Policy freshness gate
  2. KYC-aware rollout kontrolü
  3. Agreement/changelog watcher
