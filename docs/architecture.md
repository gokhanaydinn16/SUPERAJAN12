# Mimari Özeti

## Katmanlar

1. `domain.py`: kanonik veri modelleri
2. `research.py`: advisory suggestion üretir
3. `risk.py`: deterministik izin/ret mantığı
4. `execution.py`: paper order lifecycle
5. `storage.py`: SQLite audit ve timeline
6. `http_api.py`: operatör yüzeyi
7. `app.py`: orkestrasyon

## Akış

1. Market validator örnek market snapshot üretir.
2. Research ajanı structured suggestion üretir.
3. Risk motoru suggestion'dan türeyen intent'i kabul ya da reddeder.
4. Kabul edilen intent paper execution katmanına gider.
5. Fill ve position güncellemeleri event log'a yazılır.
6. Dashboard ve API bu kayıtları okuyarak canlı durumu gösterir.
