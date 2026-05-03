# Shadow Mode ve Canary Geçiş Planı

Geçiş zinciri:

`historical replay -> paper -> testnet/demo -> canary live -> scaled live`

Temel kural:

- Üst stage'e yalnızca ölçütler sağlanırsa geçilir.
- Her stage için rollback kuralları vardır.
- Ölçütler bozulursa otomatik geri dönüş açık kalır.

## 1. Historical Replay

- Amaç: Veri, risk ve execution akışını geçmiş veri üzerinde doğrulamak.
- Ölçütler: Çoklu rejim testi, yüksek PnL explained ratio, tam determinism, sıfır risk bypass.
- Rollback: Determinism bozulursa veya position drift çıkarsa stage başarısız.

## 2. Paper

- Amaç: Canlıya yakın veri akışında gerçek emir göndermeden operasyonel davranışı doğrulamak.
- Ölçütler: Kesintisiz çalışma, kill switch doğrulaması, sıfır duplicate-order incident, sıfır uncapped exposure.
- Rollback: Order state açıklanamıyorsa veya audit log bozuluyorsa historical replay'e dönülür.

## 3. Testnet ve Demo

- Amaç: Venue API semantiklerini ve order lifecycle davranışını doğrulamak.
- Ölçütler: İki venue başarı, cancel-on-disconnect başarısı, rate-limit breach kaynaklı halt olmaması.
- Rollback: Reconcile farkı artarsa paper stage'e dönülür.

## 4. Canary Live

- Amaç: Çok sınırlı gerçek sermaye ile güvenli doğrulama.
- Sermaye sınırı: Toplam strateji sermayesinin yaklaşık yüzde 1-2'si.
- Ölçütler: Uzun süreli incident-free run, yüksek PnL explained ratio, drawdown sınırı içinde kalma.
- Rollback: Drawdown eşiği aşılırsa de-risk ve kill switch.

## 5. Scaled Live

- Amaç: Canary doğrulanan stratejiyi kademeli olarak büyütmek.
- Ölçütler: Her sermaye artışında kritik risk olayı sıfır, reconcile farkı sınır içinde.
- Rollback: Başarısız kademe bir önceki güvenli sermaye seviyesine iner.

## Ortak Gate'ler

1. Teknik gate
2. Risk gate
3. Operasyon gate
4. Veri gate
5. Uyum ve policy gate
