# SuperAjan12 Roadmap

## Faz 1 - Veri okuma ve paper trading cekirdegi

- [x] Python proje yapisi
- [x] Polymarket public market connector
- [x] Market scanner agent
- [x] Risk engine v1
- [x] CLI scan komutu
- [x] Endpoint verification komutu
- [x] Orderbook midpoint/spread fallback
- [x] JSON audit log
- [x] SQLite veri kaydi
- [x] Resolution Agent v1
- [x] Probability Agent baseline v1
- [x] Paper Portfolio / paper position defteri
- [x] Reporting komutu
- [x] Safe-mode / kill-switch iskeleti
- [x] Temel testler
- [ ] Polymarket endpoint formatlarini kullanici ortaminda canli calisma ile dogrula
- [ ] Orderbook token id eslestirmesini canli veride sertlestir

## Faz 2 - Dogrulama katmani

- [x] Kalshi market data connector
- [x] Binance BTC/ETH/SOL referans verisi
- [x] OKX referans verisi
- [x] Coinbase spot referans verisi
- [x] Kaynak tutarsizligi alarmi v1
- [x] Cross-market event mapping v1
- [x] Kalshi-Polymarket benzer market eslestirme skoru v1
- [x] Reference check sonucunu scanner risk kararina bagla

## Faz 3 - Ajan kalitesi

- [x] Resolution Agent v1
- [x] Probability Agent baseline v1
- [x] Liquidity Agent v2
- [x] News Reliability Agent v1
- [x] Social Signal Agent v1
- [x] Smart Wallet Intelligence Agent v1 placeholder
- [x] Manipulasyon riski skoru v1

## Faz 4 - Shadow trading

- [x] Paper position defteri v1
- [x] Canli veri ile emir gondermeden karar kaydi iskeleti
- [x] Karar-sonuc performans mark-to-market iskeleti
- [x] Strateji skor sistemi v1
- [x] Model version tracking v1
- [ ] Shadow outcomes CLI komutu

## Faz 5 - Kontrollu canli test

- [x] API key secret manager iskeleti
- [ ] Live execution connector
- [x] Live execution guard
- [x] Kill-switch iskeleti
- [x] Reconciliation Agent iskeleti
- [ ] Kucuk sermaye limitleri
- [x] Manual approval gate

## Degismez kurallar

- Varsayilan mod paper mode.
- Risk motoru onay vermeden emir yok.
- Resolution belirsizse islem yok.
- Likidite yetersizse islem yok.
- Referans fiyat kaynaklari fazla saparsa kripto olay sinyalleri guvensiz sayilir.
- Manipulasyon riski yuksekse islem yok.
- Haber/kaynak guveni dusukse islem yok veya watch.
- Sosyal hype tek basina edge degildir.
- Cuzdan sinyali gercek veri baglanmadan edge uretmez.
- Live mode bile secret + manual approval + safe-mode kontrolu gecmeden emir gonderemez.
- Safe-mode aktifse yeni islem yok.
- Canli sistem kendi kodunu degistirmez.
- Model gercek edge uretmedikce sahte guvenle islem acmaz.
