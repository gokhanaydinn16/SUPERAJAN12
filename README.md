# superajan12

Polymarket merkezli, coklu veri kaynagi ile dogrulama yapan, risk kontrollu otonom prediction market ajan sistemi.

## Ilk hedef

Bu repo once canli para kullanmadan calisacak bir cekirdek kurar:

1. Polymarket marketlerini okur.
2. Fiyat, spread, hacim ve likidite olcer.
3. Resolution metnini ve risk bayraklarini kaydeder.
4. Risk motorundan gecmeyen marketlerde islem acmaz.
5. Paper trading sinyali uretir.
6. Her karari audit trail olarak loglar.

## Ana prensip

> Once sermayeyi koru, sonra firsat ara.

Canli emir motoru basit, disiplinli ve risk motoruna bagli kalacak. Ajanlar dusunecek; risk motoru izin verecek; emir motoru sadece onayli emri uygulayacak.

## Mimari

```text
Polymarket market data
        |
Market Scanner Agent
        |
Resolution + Liquidity + Probability checks
        |
Risk Engine
        |
Paper Trading Engine
        |
Audit log + report
```

Ilk asamada canli emir yoktur. Varsayilan mod `paper` modudur.

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
python -m superajan12.cli scan --limit 25
```

## Guvenlik

- API keyler repoya yazilmaz.
- Varsayilan mod paper trading'dir.
- Risk motoru onay vermeden emir olusmaz.
- Resolution belirsizse islem yoktur.
- Likidite yetersizse islem yoktur.
- Safe-mode aktifse yeni karar uretilmez.

## Yol haritasi

- Faz 1: Polymarket veri okuma + market puanlama + paper trading.
- Faz 2: Resolution agent + haber/kaynak dogrulama.
- Faz 3: Kalshi, Binance, OKX, Coinbase veri katmani.
- Faz 4: Shadow trading.
- Faz 5: Kucuk sermaye ile kontrollu canli test.
