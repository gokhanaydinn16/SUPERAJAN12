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
