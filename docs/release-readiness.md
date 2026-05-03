# Release Readiness Gates

Bu doküman, sistemi canlı sermayeye açmadan önce ölçülebilir koşullar koyar. Her gate bir metriğe bağlanır; test/paper ortamı bu metrikleri ürettiğinde ancak bir sonraki aşamaya geçilir.

1. **Stale Rate (< %5)** – market validator’ın 100 döngüden en fazla %5’inde stale veri veya heartbeat kaybı olmamalı. `ReadinessTracker.record_cycle(stale=True)` ile sayılır ve `snapshot().stale_rate` üzerinden kontrol edilir.

2. **Duplicate Order Incidence (< %2)** – aynı intent ID art arda gelirse risk gate bu durumu `duplicate=True` ile işaretler; `snapshot().duplicate_rate` %2’yi aşmadan üretim canary’a ilerlenmez.

3. **PnL Explained Ratio (> %80)** – research + execution pipeline’ı fill sonrası PnL’in en az %80’ini açıklar olmalı. `pnl_explained` değeri bu oran için kullanılır; `ReadinessThresholds.min_pnl_explained` ile beslenen gate alt eşik altında kalırsa kod kademe olarak geri alınır.

4. **Fill Quality (> 95%)** – execution engine’daki paper fill’ler planlanan fiyatlara yakın olmalı. `fill_quality` değeri (örneğin slippage inverse) ortalaması `ReadinessThresholds.min_fill_quality` değerinin altında ise canary durdurulur.

5. **Incident-Free Run (>= 5 cycles)** – `incident` bayrağı varsa kırılganlık var. `incident_free_streak` 5’i aşmadan sonraki environment (testnet, canary, scaled live) adımına geçilmeyecek.

Her gate karşılanmadığında `ReadinessTracker.is_ready` False döner; ana loop bu sonucu loglar, event store’a `ready=false` yazılıp rollout durdurulur. Gate’ler production geçiş planına hizmet eden `release-readiness.md`’de dokümante edilir ve `readiness.py`’deki modelle senkron çalışır.
