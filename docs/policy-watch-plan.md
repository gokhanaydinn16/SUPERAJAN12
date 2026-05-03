# Policy Watch Plan

Bu belge policy watcher katmanının nasıl işlediğini, hangi snapshot yapısının kullanıldığını ve rollout sinyallerini tanımlar.

1. **Girdi**: `/workspace/src/agent_os/venue_policy.py` kayıtlı policy profilleri.
2. **Çıktı**: `PolicyWatcher.rollout_signal()` yöntemi, policy_fresh, changes_detected, ve mesaj içeren sözlük döner.
3. **Snapshot stratejisi**: Her capture çağrısında JSON dosyasına yazılır; önceki snapshot karşılaştırılır; fark varsa `changes_detected` true olur.
4. **Stale tespiti**: Son snapshot güncellenmiş zamana göre `stale_after` eşik değerinden eskiyse `policy_fresh` false olur.
5. **Rollback sinyali**: Policy değişimi veya stale durum `message` içinde açık şekilde belirtilir ve rollout gate bu sinyali kullanır.
6. **Dokümantasyon**: Bu plan dosyası, kod içindeki `PolicyWatcher` sınıfıyla senkron tutulmalı.
