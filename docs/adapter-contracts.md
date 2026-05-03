# Adapter Contracts

Tarih: 3 Mayıs 2026

Kapsam: Deribit ve Binance USD-M Futures için ilk request ve response sözleşmeleri.

## Repo İçi Ortak Fonksiyonlar

1. `fetch_order_book_snapshot(symbol)`
2. `stream_order_book_diff(symbol, speed)`
3. `submit_order(intent)`
4. `cancel_order(order_ref)`
5. `fetch_position(symbol)`
6. `heartbeat()`

## Normalize Dönüş Tipleri

- `Snapshot`: `symbol`, `venue`, `last_update_id`, `bids`, `asks`, `ts`
- `DepthDiff`: `symbol`, `first_id`, `final_id`, `prev_final_id`, `bids`, `asks`, `ts`
- `SubmitAck`: `order_id`, `client_id`, `status`, `filled_qty`, `avg_price`, `raw_state`
- `CancelAck`: `order_id`, `status`, `raw_state`
- `PositionState`: `symbol`, `size`, `side`, `entry_price`, `mark_price`, `unrealized_pnl`, `leverage`
- `HeartbeatState`: `ok`, `latency_ms`, `server_time`

## Deribit

- Snapshot: `public/get_order_book`
- Diff: `book.{instrument}.{interval}`
- Submit: `private/buy` veya `private/sell`
- Cancel: `private/cancel`
- Position: `private/get_position`
- Heartbeat: `public/set_heartbeat` veya `public/get_time`

Uygulama notu:

- `prev_change_id` zinciri kırılırsa local book reset ve yeni snapshot zorunlu.

## Binance USD-M Futures

- Snapshot: `GET /fapi/v1/depth`
- Diff: `<symbol>@depth`, `<symbol>@depth@500ms`, `<symbol>@depth@100ms`
- Submit: `POST /fapi/v1/order`
- Cancel: `DELETE /fapi/v1/order`
- Position: `GET /fapi/v3/positionRisk`
- Heartbeat: WS ping/pong ve `GET /fapi/v1/time`

Uygulama notu:

- `U/u/pu` zinciri bozulursa snapshot yeniden çekilmeli.

## İlk Uygulama Sırası

1. Deribit JSON-RPC execution ve market data
2. Binance diff-depth ve position risk

## Normalizasyon Kuralı

Venue adapter her zaman normalize tip döndürür. Ham payload saklanabilir ama risk ve execution çekirdeği normalize yüzeyi görür.
