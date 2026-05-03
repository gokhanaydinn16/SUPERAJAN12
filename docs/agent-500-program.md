# Agent 500 Program

Bu belge 500 bağımsız ajan görevini tanımlar. Çalışma ortamı aynı anda 500 ajan çalıştırmadığı için bunlar dalgalar halinde yürütülür. Her ajan tek, net ve çakışmasız bir sorumluluğa sahiptir.

## Çalıştırma Kuralı

- 500 görev tanımlıdır.
- Eşzamanlı çalışan ajan sayısı ortam limitine göre dalgalar halinde seçilir.
- Her dalga sonunda sadece doğrulanmış çıktılar ana koda girer.

## Domain 1: Program ve Mimari

A001: Kanonik domain modelini ince ayarla  
A002: Modül bağımlılık haritasını çıkar  
A003: Config matrisi tasarla  
A004: Environment profilleri tanımla  
A005: Stage geçiş politikasını sertleştir  
A006: Merge ve ownership kurallarını yaz  
A007: Backlog taxonomy çıkar  
A008: Refactor sınırlarını belirle  
A009: Cross-module event contract’larını doğrula  
A010: Hot path ve cold path ayrımı yap  
A011: Capability registry mimarisini genişlet  
A012: Feature flag yapısını tasarla  
A013: Canary kontrol akışını mimariye bağla  
A014: Shadow mode davranışını normalize et  
A015: Release artifact yapısını tanımla  
A016: Risk, execution, research sınırlarını doğrula  
A017: Policy-sensitive venue farklarını mimariye işle  
A018: Multi-venue future state planını çıkar  
A019: Kod organizasyonunun sonraki faz hedefini yaz  
A020: Final mimari kontrol listesini oluştur  

## Domain 2: Deribit Venue

A021: Deribit auth kontratını yaz  
A022: Deribit order book snapshot adapter’ını tasarla  
A023: Deribit diff stream adapter’ını tasarla  
A024: Deribit heartbeat akışını tanımla  
A025: Deribit buy mapper’ını yaz  
A026: Deribit sell mapper’ını yaz  
A027: Deribit cancel mapper’ını yaz  
A028: Deribit get_position mapper’ını yaz  
A029: Deribit normalize response modeli yaz  
A030: Deribit reduce_only eşlemesini doğrula  
A031: Deribit post_only eşlemesini doğrula  
A032: Deribit tif eşlemesini doğrula  
A033: Deribit error code normalizer yaz  
A034: Deribit reconnect davranışını tanımla  
A035: Deribit rate-limit guard tasarla  
A036: Deribit testnet profile’ını bağla  
A037: Deribit paper-to-testnet testlerini yaz  
A038: Deribit reconciliation kontrolü ekle  
A039: Deribit telemetry alanlarını tanımla  
A040: Deribit readiness gate’lerini çıkar  

## Domain 3: Binance USD-M Futures

A041: Binance auth signing katmanını yaz  
A042: Binance `/depth` snapshot mapper’ını yaz  
A043: Binance diff-depth parser’ı yaz  
A044: Binance `U/u/pu` chain validator yaz  
A045: Binance gap recovery akışını kur  
A046: Binance order submit mapper’ını yaz  
A047: Binance cancel mapper’ını yaz  
A048: Binance position risk mapper’ını yaz  
A049: Binance listen key/user stream planını yaz  
A050: Binance order status normalization yaz  
A051: Binance mark price feed mapper’ını yaz  
A052: Binance funding feed mapper’ını yaz  
A053: Binance rate-limit telemetry ekle  
A054: Binance desync metric ekle  
A055: Binance stale-lock testleri yaz  
A056: Binance partial fill davranışını doğrula  
A057: Binance testnet env profile’ını bağla  
A058: Binance reconnect ve replay akışını yaz  
A059: Binance readiness gate’lerini çıkar  
A060: Binance incident rollback akışını yaz  

## Domain 4: Coinbase Advanced Trade

A061: Coinbase auth contract yaz  
A062: Coinbase preview request modeli yaz  
A063: Coinbase preview response normalizer yaz  
A064: Coinbase submit order mapper’ını yaz  
A065: Coinbase cancel order mapper’ını yaz  
A066: Coinbase fills fetch mapper’ını yaz  
A067: Coinbase positions/holdings modeli yaz  
A068: Coinbase portfolio segregation desteğini ekle  
A069: Coinbase websocket market data planını yaz  
A070: Coinbase sandbox profile’ını bağla  
A071: Coinbase preview-pass metric ekle  
A072: Coinbase preview failure rollback kuralı yaz  
A073: Coinbase readiness gate’lerini çıkar  
A074: Coinbase permission matrix’ini ekle  
A075: Coinbase env-specific behavior notlarını kodla  
A076: Coinbase pre-trade validation tests yaz  
A077: Coinbase policy edge case’lerini topla  
A078: Coinbase telemetry mapping yaz  
A079: Coinbase adapter contract tests yaz  
A080: Coinbase release checklist çıkar  

## Domain 5: OKX

A081: OKX auth contract yaz  
A082: OKX demo/live capability ayrımını kodla  
A083: OKX snapshot mapper’ını yaz  
A084: OKX diff stream parser’ı yaz  
A085: OKX order submit mapper’ını yaz  
A086: OKX cancel mapper’ını yaz  
A087: OKX position mapper’ını yaz  
A088: OKX KYC gate kuralını bağla  
A089: OKX policy freshness control ekle  
A090: OKX changelog watcher hook’u yaz  
A091: OKX agreement watcher hook’u yaz  
A092: OKX policy-sensitive rollout kuralını yaz  
A093: OKX demo profile’ını bağla  
A094: OKX live-disable default’ını yaz  
A095: OKX telemetry alanlarını bağla  
A096: OKX adapter contract tests yaz  
A097: OKX incident policy rollback akışını yaz  
A098: OKX readiness gate’lerini çıkar  
A099: OKX operator warning surface’ını ekle  
A100: OKX final integration checklist çıkar  

## Domain 6: Market State Core

A101: Unified snapshot type’ını sertleştir  
A102: Unified diff type’ını sertleştir  
A103: Local order book state machine yaz  
A104: Book reset akışını yaz  
A105: Sequence gap event modeli ekle  
A106: Checksum abstraction ekle  
A107: Multi-venue freshness tracking yaz  
A108: Heartbeat monitor genişlet  
A109: Mark price channel ekle  
A110: Funding state channel ekle  
A111: OI state channel ekle  
A112: Liquidation event type ekle  
A113: Tick-to-feature latency metriği ekle  
A114: Clock skew ölçümünü ekle  
A115: Book desync explained report yaz  
A116: Snapshot recovery tests yaz  
A117: Diff replay tests yaz  
A118: Sequence anomaly alarms ekle  
A119: Venue-specific parser registry yaz  
A120: Market-state final readiness check çıkar  

## Domain 7: Execution Core

A121: Submit path refactor et  
A122: Preview-before-submit zincirini sertleştir  
A123: Client order id stratejisi ekle  
A124: Idempotency key stratejisi ekle  
A125: Retry policy yaz  
A126: Cancel-on-disconnect sertleştir  
A127: Partial fill accumulation yaz  
A128: Filled/open/cancelled state transitions yaz  
A129: Reject reason normalizer ekle  
A130: Execution latency metric ekle  
A131: Preview bypass detection ekle  
A132: Venue response raw_state saklama ekle  
A133: Order amend future hook ekle  
A134: Execution replay support ekle  
A135: Duplicate submission prevention yaz  
A136: Open order restore flow ekle  
A137: Cancel reconciliation logic yaz  
A138: Submit/cancel integration tests yaz  
A139: Cross-venue execution abstraction review yap  
A140: Execution go-live checklist çıkar  

## Domain 8: Risk Core

A141: Max position clamp sertleştir  
A142: Max notional clamp sertleştir  
A143: Max leverage clamp sertleştir  
A144: Stale data lock sertleştir  
A145: Duplicate intent guard iyileştir  
A146: Order-rate throttle ekle  
A147: Cancel-rate throttle ekle  
A148: Kill switch escalation levels yaz  
A149: Venue-specific risk overrides yaz  
A150: Reduce-only enforcement yaz  
A151: Liquidation distance guard ekle  
A152: Funding exposure guard ekle  
A153: Correlation exposure guard ekle  
A154: Daily loss budget ekle  
A155: Session loss lock ekle  
A156: Manual operator override policy yaz  
A157: Risk event taxonomy yaz  
A158: Risk regression tests genişlet  
A159: Risk breach reporting surface ekle  
A160: Risk readiness checklist çıkar  

## Domain 9: Portfolio ve Capital

A161: Strategy-level capital budget yaz  
A162: Venue-level capital budget yaz  
A163: Global exposure ledger yaz  
A164: Margin buffer allocator yaz  
A165: Inventory skew controller yaz  
A166: Position netting policy yaz  
A167: Venue cash segregation yaz  
A168: Unrealized/realized pnl ledger yaz  
A169: Capital-at-risk metric ekle  
A170: Capital ladder for canary yaz  
A171: Strategy cooldown policy ekle  
A172: Loss recovery lock yaz  
A173: Cross-strategy conflict resolver yaz  
A174: Manual de-risk workflow yaz  
A175: Portfolio health score ekle  
A176: Portfolio dashboard cards ekle  
A177: Capital reconciliation report yaz  
A178: Budget enforcement tests yaz  
A179: Venue transfer policy notlarını çıkar  
A180: Portfolio final readiness gate yaz  

## Domain 10: Research Platform

A181: Experiment registry yaz  
A182: Dataset manifest yapısı yaz  
A183: Feature extraction pipeline yaz  
A184: Labeling hooks ekle  
A185: Walk-forward runner yaz  
A186: Backtest result schema yaz  
A187: Slippage-adjusted metric seti yaz  
A188: Fill quality evaluator yaz  
A189: PnL explained ratio hesaplayıcı yaz  
A190: Regime-tagged evaluation yaz  
A191: Experiment comparison view yaz  
A192: Overfit detection heuristic yaz  
A193: Research run audit log yaz  
A194: Alpha registry dosya yapısı yaz  
A195: Research to shadow handoff contract’ı yaz  
A196: Replay dataset validator yaz  
A197: Research CI smoke tests ekle  
A198: Evaluation dashboard contract yaz  
A199: Research storage retention planı yaz  
A200: Research platform completion gate yaz  

## Domain 11: Alpha 1 Microstructure

A201: Imbalance feature tanımı yaz  
A202: Microprice feature tanımı yaz  
A203: Spread compression feature yaz  
A204: Queue pressure proxy yaz  
A205: Short-horizon target labels yaz  
A206: Replay scorer yaz  
A207: Hit-rate metric yaz  
A208: Adverse selection metric yaz  
A209: Alpha decay metric yaz  
A210: Entry filter policy yaz  
A211: Exit rule family tasarla  
A212: Slippage sensitivity testleri yaz  
A213: Regime breakdown raporu yaz  
A214: Outlier handling stratejisi yaz  
A215: Feature drift detector ekle  
A216: Paper shadow evaluator ekle  
A217: Testnet shadow evaluator ekle  
A218: Risk-compatible sizing hook ekle  
A219: Go/No-Go threshold çıkar  
A220: Microstructure alpha dossier yaz  

## Domain 12: Alpha 2 Funding/Basis

A221: Funding feed collector yaz  
A222: Basis feed collector yaz  
A223: Carry signal feature seti yaz  
A224: OI-conditioned carry feature ekle  
A225: Volatility-conditioned carry filter yaz  
A226: Net carry metric yaz  
A227: Drawdown profile analyzer yaz  
A228: Funding normalization detector yaz  
A229: Multi-venue carry comparison yaz  
A230: Carry regime classifier yaz  
A231: Entry windows logic yaz  
A232: Exit windows logic yaz  
A233: Fee-aware evaluator yaz  
A234: Paper carry shadow test yaz  
A235: Replay carry scorecard yaz  
A236: Stress window analysis yaz  
A237: Risk budget integration hook yaz  
A238: Carry readiness threshold çıkar  
A239: Carry failure mode catalog yaz  
A240: Carry alpha dossier yaz  

## Domain 13: Alpha 3 Event/Liquidation

A241: Liquidation event schema yaz  
A242: Volatility shock detector yaz  
A243: Tape acceleration feature yaz  
A244: Depth collapse feature yaz  
A245: Event window evaluator yaz  
A246: Tail-loss metric yaz  
A247: CVaR profile hesaplayıcı yaz  
A248: False-break detector yaz  
A249: Latency penalty analysis yaz  
A250: Entry cooldown logic yaz  
A251: Stop policy family yaz  
A252: Event-driven exit logic yaz  
A253: Replay liquidation stress suite yaz  
A254: Paper shadow event suite yaz  
A255: Regime vulnerability report yaz  
A256: Signal freshness gate yaz  
A257: Risk scaling hook yaz  
A258: No-trade zone detector yaz  
A259: Event alpha go/no-go çıkar  
A260: Event alpha dossier yaz  

## Domain 14: Alpha 4 Regime Selector

A261: Trend regime detector yaz  
A262: Mean-reversion regime detector yaz  
A263: Volatility regime detector yaz  
A264: Liquidity regime detector yaz  
A265: Meta-selector feature seti yaz  
A266: Regret metric yaz  
A267: Strategy switching cost metric yaz  
A268: Transition lag metric yaz  
A269: Selector calibration logic yaz  
A270: Selector confidence model yaz  
A271: Selector fallback policy yaz  
A272: Selector shadow tests yaz  
A273: Replay selector evaluation yaz  
A274: Paper selector evaluation yaz  
A275: Overfit/instability detector yaz  
A276: Regime visualization surface yaz  
A277: Risk handoff contract yaz  
A278: Selector readiness threshold çıkar  
A279: Selector failure-mode notes yaz  
A280: Regime alpha dossier yaz  

## Domain 15: Advisory AI

A281: News summarizer schema yaz  
A282: Social signal schema yaz  
A283: On-chain signal schema yaz  
A284: Macro signal schema yaz  
A285: Confidence calibration heuristic yaz  
A286: Contradiction detector yaz  
A287: Narrative drift detector yaz  
A288: Advisory output validator yaz  
A289: JSON schema guard yaz  
A290: Prompt versioning planı yaz  
A291: Prompt risk policy yaz  
A292: Shadow-only AI enforcement yaz  
A293: AI decision audit trail yaz  
A294: AI suggestion comparison tool yaz  
A295: Hallucination containment rule seti yaz  
A296: Operator explainability surface yaz  
A297: AI disable switch ekle  
A298: AI regression tests yaz  
A299: Advisory AI readiness gate yaz  
A300: Advisory AI dossier yaz  

## Domain 16: Data Platform ve Feature Store

A301: Historical dataset folder yapısı yaz  
A302: Feature store schema yaz  
A303: Feature versioning planı yaz  
A304: Replay input manifest yaz  
A305: Dataset lineage notasyonu yaz  
A306: Missing data policy yaz  
A307: Null handling policy yaz  
A308: Time alignment policy yaz  
A309: Cross-venue clock normalization yaz  
A310: Compression and retention planı yaz  
A311: Feature quality report yaz  
A312: Data freshness report yaz  
A313: Replay export interface yaz  
A314: Event-to-feature bridge yaz  
A315: Feature drift alarm yaz  
A316: Dataset audit log yaz  
A317: Data smoke tests yaz  
A318: Offline/online parity checks yaz  
A319: Feature store release gate yaz  
A320: Data platform dossier yaz  

## Domain 17: Storage ve Replay

A321: Event store schema genişlet  
A322: Replay cursor modeli ekle  
A323: Batch event export yaz  
A324: Event filtering API yaz  
A325: Replay restore state yaz  
A326: Storage compaction strategy yaz  
A327: Retention and archival policy yaz  
A328: Audit export formatı yaz  
A329: Storage durability checks yaz  
A330: WAL and locking review yap  
A331: Corrupt event detection yaz  
A332: Recovery after crash flow yaz  
A333: Replay determinism tests yaz  
A334: Storage latency telemetry ekle  
A335: Large event handling yaz  
A336: Snapshotting strategy yaz  
A337: Read-mostly query optimization yaz  
A338: Timeline query improvements yaz  
A339: Storage readiness gate yaz  
A340: Storage dossier yaz  

## Domain 18: Observability ve Alerting

A341: Metric namespace tasarla  
A342: Health summary standardını yaz  
A343: Risk dashboard metricleri yaz  
A344: Venue telemetry metricleri yaz  
A345: Research metricleri yaz  
A346: Portfolio metricleri yaz  
A347: Readiness metricleri yaz  
A348: Alert thresholds yaz  
A349: Error taxonomy yaz  
A350: Incident severity mapping yaz  
A351: Log enrichment alanları ekle  
A352: Timeline export surface yaz  
A353: Kill-switch visibility yüzeyi yaz  
A354: Venue desync alarmı ekle  
A355: Reconciliation alarmı ekle  
A356: Policy freshness alarmı ekle  
A357: AI contradiction alarmı ekle  
A358: Heartbeat loss alarmı ekle  
A359: Observability readiness gate yaz  
A360: Observability dossier yaz  

## Domain 19: Dashboard ve Product Surface

A361: Dashboard IA tasarla  
A362: Health panel contract yaz  
A363: Risk panel contract yaz  
A364: Position panel contract yaz  
A365: Orders timeline contract yaz  
A366: Suggestions panel contract yaz  
A367: Readiness panel contract yaz  
A368: Venue selector davranışı yaz  
A369: Kill switch control yüzeyi yaz  
A370: Stage promotion UX contract yaz  
A371: Reconciliation panel yaz  
A372: Audit log panel yaz  
A373: Research panel yaz  
A374: Strategy comparison panel yaz  
A375: Canary indicators panel yaz  
A376: Alert banner system yaz  
A377: Mobile fallback layout yaz  
A378: Dashboard interaction smoke tests yaz  
A379: Product surface readiness gate yaz  
A380: Product surface dossier yaz  

## Domain 20: Compliance ve Policy

A381: Venue changelog watcher tasarla  
A382: API agreement watcher tasarla  
A383: KYC requirement tracker yaz  
A384: Policy diff report yaz  
A385: Rollout halt on policy drift yaz  
A386: Operator acknowledgement flow yaz  
A387: Audit evidence export yüzeyi yaz  
A388: Account boundary notes yaz  
A389: Secret rotation process yaz  
A390: Compliance state dashboard yaz  
A391: Region/jurisdiction gating notları yaz  
A392: Managed account boundary kontrolü yaz  
A393: Retention policy dokümanı yaz  
A394: Policy watcher tests yaz  
A395: Compliance readiness gate yaz  
A396: OKX special controls checklist yaz  
A397: Live enable prerequisites listesi yaz  
A398: Agreement audit log ekle  
A399: Compliance handoff paketi yaz  
A400: Compliance dossier yaz  

## Domain 21: Security

A401: Secret manager interface tasarla  
A402: Env var hygiene policy yaz  
A403: Credential scope matrisi yaz  
A404: API key permission minimization yaz  
A405: Operator action authorization flow yaz  
A406: Session boundary notes yaz  
A407: Data redaction policy yaz  
A408: Audit log secret scrubber yaz  
A409: Production env separation policy yaz  
A410: Testnet/prod secret split yaz  
A411: Local development secret policy yaz  
A412: Access review checklist yaz  
A413: Security smoke tests yaz  
A414: Emergency secret revoke playbook yaz  
A415: Security readiness gate yaz  
A416: Live kill authority matrix yaz  
A417: Operator least privilege surface yaz  
A418: Sensitive config linter yaz  
A419: Security evidence bundle yaz  
A420: Security dossier yaz  

## Domain 22: Recovery ve Chaos

A421: Restart recovery flow yaz  
A422: Event replay restore tests yaz  
A423: Venue disconnect scenario yaz  
A424: WS reconnect chaos test yaz  
A425: Snapshot corruption chaos test yaz  
A426: Storage lock contention test yaz  
A427: Partial dependency failure test yaz  
A428: Clock drift test yaz  
A429: Stale data storm scenario yaz  
A430: Duplicate event storm scenario yaz  
A431: Order reject burst scenario yaz  
A432: Cancel timeout scenario yaz  
A433: Incident auto-halt policy yaz  
A434: Recovery readiness checklist yaz  
A435: Operator restart playbook yaz  
A436: Replay-after-crash smoke test yaz  
A437: Chaos result reporter yaz  
A438: Degrade mode UX yüzeyi yaz  
A439: Resilience readiness gate yaz  
A440: Resilience dossier yaz  

## Domain 23: Testing ve CI

A441: Unit test matrixini çıkar  
A442: Integration test matrixini çıkar  
A443: Adapter contract tests yaz  
A444: Risk regression suite yaz  
A445: Replay determinism suite yaz  
A446: Dashboard smoke tests yaz  
A447: CI workflow planı yaz  
A448: Minimal dependency CI yolu yaz  
A449: Coverage hedeflerini tanımla  
A450: Test data fixtures yaz  
A451: Golden files strategy yaz  
A452: Failure triage notes yaz  
A453: Pre-merge checks listesi yaz  
A454: Post-merge verification flow yaz  
A455: Manual release verification checklist yaz  
A456: CI alerting integration planı yaz  
A457: Flaky test quarantine policy yaz  
A458: Test readiness gate yaz  
A459: CI hardening backlog yaz  
A460: Testing dossier yaz  

## Domain 24: Deployment ve Runtime

A461: Packaging stratejisi yaz  
A462: Single-process runtime profile yaz  
A463: Multi-process future plan yaz  
A464: Container profile notları yaz  
A465: Service unit örneği yaz  
A466: Runtime config docs yaz  
A467: Port management strategy yaz  
A468: Health endpoint rollout yaz  
A469: Graceful shutdown planı yaz  
A470: Data directory policy yaz  
A471: Log directory policy yaz  
A472: Backup/restore runtime notes yaz  
A473: Deployment smoke test yaz  
A474: Environment boot checklist yaz  
A475: Prod readiness gate yaz  
A476: Testnet deploy gate yaz  
A477: Canary deploy gate yaz  
A478: Rollback deploy flow yaz  
A479: Runtime ops handoff yaz  
A480: Deployment dossier yaz  

## Domain 25: Final Integration

A481: Tüm exit criteria’ları tek yerde topla  
A482: Roadmap -> backlog -> code bağlantısını doğrula  
A483: Release readiness master sheet yaz  
A484: Open risk register yaz  
A485: Cross-team dependency listesi yaz  
A486: Final architecture review yap  
A487: Final risk review yap  
A488: Final execution review yap  
A489: Final research review yap  
A490: Final portfolio review yap  
A491: Final observability review yap  
A492: Final compliance review yap  
A493: Final security review yap  
A494: Final resilience review yap  
A495: Final product review yap  
A496: Final testing review yap  
A497: Final deployment review yap  
A498: Merge captain checklist çıkar  
A499: Live enable checklist çıkar  
A500: Project completion dossier yaz  

## Kullanım

- Bu dosya görev bankasıdır.
- Her ajan bir satırın owner’ı olur.
- Dalgalar halinde işlenir.
- Tamamlandıkça ilgili görev repo içindeki code, doc veya test artefaktına bağlanır.
