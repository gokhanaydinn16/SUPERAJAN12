# Research Notes

Bu doküman research ajanı katmanının amacını, sinyal modelini ve deterministik yürütme çekirdeğine verdiği önerileri açıklar.

## Hedef
- Haber, sosyal, on-chain ve rejim (macro/olay) girdilerini bağımsız sinyaller olarak ele almak.
- Her sinyali `ResearchSignal` içinde normalize edilmiş `severity`, `source`, `description` ve `timestamp` ile temsil etmek.
- Sadece önceden tanımlanmış eylem tiplerinden (`increase`, `decrease`, `neutral`, `halt`) oluşan, şema-doğrulanmış `DecisionSuggestion` nesneleri üretmek.
- Oluşturulan öneriyi confidence/ rationale ile birlikte kaydedip deterministik çekirdeğe iletmek; böylece AI katmanı sadece onaylanmış öneriler sunar.

## Veri Kaynakları ve Mock Akış
1. **News**: Regülasyon/duyuru içerikleri `severity` ortalamasını yüksek tutarak risk küçültme sinyali üretir.
2. **Social**: Reddit/Twitter gibi platformlardan volatilite trendi izlenir, `severity` orta düzeydedir ve sinyal çeşitliliği sağlar.
3. **On-chain**: Büyük stablecoin transferleri veya borsa girişleri, düşük gecikme ile risk algısını yükseltir.
4. **Regime**: Makro kararlar, politika duyuruları ve planlı hacim artışları gibi kontekstual veriler.

Mock akış `sample_workflow` fonksiyonunda dört kaynaktan sinyal üretir. Her bir sinyal tek `ResearchSignal` nesnesi olup deterministik ajan `propose` çağrısı ile öneriye dönüştürülür.

## Karar Üretimi ve Doğrulama
- Ajan severity ortalamasına göre `action` belirler: yüksek severity `decrease`, düşük `increase`, orta aralık `neutral`.
- Confidence `0.1-1.0` aralığında normalleştirilir; overflow ihtimaline karşı min/max clamp yapılır.
- `DecisionSuggestion` sadece en az bir sinyal içeren, confidence aralığı kontrol edilmiş ve `action` literal'leriyle uyumlu nesnelere izin verir.
- Oluşan öneri `history` içine kaydedilir; deterministik çekirdek bu geçmişten ölçümler alabilir, shadow execution ve kill switch için referans olur.

## Integre Olma Notları
- Deterministik execution çekirdeği, önerileri `DecisionSuggestion` yapısına göre alacak; `signal_summary` içindekiler risk/duraklama mantığını besler.
- SIGINT / kill switch senaryolarında `action="halt"` öneriyi destekleyecek; hazır `sample_workflow` şu anda sadece diğer üç eylemle çalışıyor ama mimari `halt` eklemeye açık.
- Öneri confidence'ı 0.5'in altına düştüğünde determ çekirdekte `shadow mode` veya ek vaka analizi tetiklenebilir.

## Açık Sorular ve Bir Sonraki Adım
1. Gerçek veri bağlayıcıları için queue/stream adaptörü (örn. WebSocket, REST polling) eklenmeli.
2. Confidence hesaplama modellerini RL/LLM ile hizalamak için weight parametreleri belirlenmeli (örneğin: `severity` + `source trust score`).
3. Regime/rejection sinyalleri için `halt` eylemi opsiyonu olası; bu eylem tipinin deterministik çekirdeğe nasıl kapalı olacağı kararlaştırılmalı.

Bu notlar, araştırma ajanının MVP davranışını belgeleyip sonraki fazlardaki genişletmeleri tanımlar.
