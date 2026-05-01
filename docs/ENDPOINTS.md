# Endpoint Notlari

Bu dokuman Faz 1'de kullandigimiz public Polymarket endpointlerini kaydeder.

## Gamma market kesfi

Kullanim:

```text
GET https://gamma-api.polymarket.com/markets
```

Parametreler:

```text
active=true
closed=false
limit=<n>
offset=<n>
order=volume
ascending=false
```

Amac:

- aktif marketleri bulmak
- market question/title bilgisini almak
- hacim ve likidite alanlarini okumak
- CLOB token id alanlarini yakalamak

Beklenen alanlar farkli formatlarda gelebilecegi icin connector su alanlara toleranslidir:

- `id`
- `conditionId`
- `slug`
- `question`
- `title`
- `volume`
- `volumeNum`
- `liquidity`
- `liquidityNum`
- `clobTokenIds`
- `clobTokenIDs`
- `tokenIds`
- `outcomeTokenIds`

## CLOB orderbook

Kullanim:

```text
GET https://clob.polymarket.com/book?token_id=<token_id>
```

Amac:

- YES token icin bid/ask seviyelerini okumak
- best bid, best ask, mid ve spread hesaplamak

## CLOB midpoint fallback

Kullanim:

```text
GET https://clob.polymarket.com/midpoint?token_id=<token_id>
```

Desteklenen yanit alanlari:

- `mid_price`
- `mid`
- `midpoint`

## CLOB spread fallback

Kullanim:

```text
GET https://clob.polymarket.com/spread?token_id=<token_id>
```

Desteklenen yanit alani:

- `spread`

## Scanner davranisi

1. Once full orderbook okunur.
2. Full orderbook basarisizsa midpoint okunur.
3. Spread okunur.
4. Midpoint + spread ile sentetik best bid / best ask olusturulur.
5. Bu fallback kullanilirsa `orderbook_source=midpoint_spread_fallback` kaydedilir.
6. Hicbiri okunamazsa risk motoru marketi reddeder.

## Guvenlik notu

Bu endpointler sadece public market data icin kullanilir. Faz 1'de emir imzalama, API key kullanimi veya live trading yoktur.

## Local backend API

Desktop command center ve local web/runtime katmani su endpointleri kullanir:

```text
GET  /health
GET  /sources
GET  /events
GET  /dashboard
GET  /research/tasks
GET  /markets
GET  /market-state/validate?market_id=<id>&token_id=<id>
GET  /wallet/events
GET  /strategy/scores
GET  /risk/status
GET  /execution/status
GET  /system/health
GET  /positions
GET  /audit/events
POST /scan
POST /verify-endpoints
POST /safety/enable-safe-mode
POST /safety/enable-kill-switch
POST /safety/clear
WS   /events/stream
```

### `GET /execution/status`

Bu endpoint canli emir gondermez. Yalnizca su bariyerleri gorunur hale getirir:

- manual approval durumu
- gerekli secret varligi
- reconciliation sonucu
- execution guard karari
- dry-run order preview uygunlugu

### `GET /system/health`

Bu endpoint runtime seviyesinde su bilgileri dondurur:

- backend uptime
- event history sayisi
- sqlite dosya durumu
- audit log durumu
- source health ozeti

### `WS /events/stream`

Desktop command center canli his icin backend event stream dinler. Kaynak health, scan tamamlama, audit snapshot ve benzeri backend olaylari bu kanal uzerinden akar.
