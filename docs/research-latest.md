# Güncel Araştırma Özeti

Tarih: 3 Mayıs 2026

Bu not, resmi ve güncel kaynaklardan doğrulanan dış gerçekleri mevcut sistem mimarisine bağlar.

## Doğrulanan Gerçekler

1. Deribit testnet canlıya oldukça yakın davranıyor ama üretim HFT altyapısını sunmuyor; ayrıca testnet önceden duyurulmadan bakım için kapanabiliyor.
Kaynak: Deribit Testnet ve Deribit API belgeleri.

2. Deribit test ve prod ortamlarında aynı varsayılan rate limit yaklaşımını ve kredi tabanlı limit mantığını kullanıyor.
Kaynak: Deribit testnet ve rate limits dokümantasyonu.

3. Coinbase Advanced Trade API, `v3` brokerage uçları üzerinden order, fill, account ve preview akışlarını sunuyor.
Kaynak: Coinbase Advanced Trade REST API belgeleri.

4. Coinbase Advanced Trade tarafında sandbox/prod benzer endpoint yüzeyi önemli, ama canlı davranış varsayımları üretmeden önce canlıya yakın doğrulama katmanı şart.
Bu, dokümantasyon ve önceki araştırma çıkarımlarının birleşimidir.

5. OKX tarafında API erişimi ve canlı order verme için güncel KYC gereksinimleri aktif biçimde politika konusu; resmi API agreement ve değişiklik notları bunu açıkça bağlıyor.
Kaynak: OKX API Agreement ve OKX docs changelog.

6. OKX canlı order akışında KYC Level 2 gereksinimi not edilmiş; demo trading bundan etkilenmiyor.
Kaynak: OKX docs changelog.

## Repo İçin Mühendislik Sonuçları

1. Venue adapter katmanı sadece REST/WS teknik entegrasyonu değil, venue capability ve policy bilgisi de taşımalı.
Örnek: `supports_testnet`, `supports_demo_trading`, `requires_live_kyc_level`, `public_hft_gap`.

2. Canary geçiş planı borsa bazlı olmalı.
Deribit testnet canlıya yakınlık için daha güçlü bir entegrasyon adayı, OKX ise policy/KYC gating nedeniyle capability registry ile ele alınmalı.

3. Order preview ve pre-trade validation kavramı Coinbase için ilk sınıf destek olmalı.
Mimari sonucu: execution öncesi `preview_order` veya eşdeğer arayüz hazırlanmalı.

4. Rate limit ve policy drift watcher artık sonraki faz değil, çekirdek production-hardening backlog’una alınmalı.

5. Testnet/prod eşdeğerliği venue bazında farklı olduğu için replay, paper, demo, testnet ve canary aşamaları ayrı environment tipleri olarak modellenmeli.

## Bu Turda Çıkacak Teknik İşler

1. Venue capability/policy modeli eklemek
2. Environment stage modeli eklemek
3. Policy watcher backlog’unu kod ve plan seviyesinde ilk sınıf yapmak
4. Shadow mode ve canary rollout yolunu netleştirmek
