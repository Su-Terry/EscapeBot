# EscapeBot Backlog

## 索引

* Phase 1 findings — F1-F14
* Phase 1.5 — 修 phase 1 surface 的 issues
* Phase 2 — Web 版規劃
* Phase 3+ — 主題擴展、Narrative Director
* Out of scope — 不要做的事
* Deploy lessons learned — 工程坑
* Cost monitoring — 真實 cost 追蹤

---

## Phase 1 findings

從 manual test + 真實玩家 surface 的 issues, 按優先級排序。

### 🟡 中優先級

#### F1: Puzzle 解開瞬間 narration 信號不明確

* Symptom: 輸入正確順序後 narration 說「沒有完全解開」, 然後又給鑰匙
* 修法: Turn Handler prompt 強化 success narration
* Source: Player A testing session

#### F2: 玩家在錯誤 location 嘗試 puzzle solution 沒有引導

* Symptom: 玩家在錯誤房間輸入 puzzle 解答, bot 沒有提示正確 location
* 修法: Rule Enforcer 提供 location-aware hint
* Source: Early external testing

#### F5: 缺 drop_item action type 導致詭異 narration

* Symptom: 玩家試圖丟棄物品時, schema 不支援 drop_item, LLM improvisation 變成 surreal narration
* Player quote: 「??? 好恐怖 XD」
* 評估: 某些情況形成 viral moment, 但可能導致 frustration
* 修法: 增加 drop_item action type
* Source: Engineer Tester session

### 🟢 低優先級

#### F3: 環境線索沒有持久化

* Symptom: 玩家看到線索後沒有任何 persistent note system
* 修法: phase 2 加玩家筆記功能
* Source: Early tester feedback

#### F4: 救援機制存在但不明確

* Symptom: 玩家卡關後, 世界狀態 subtly 幫助玩家
* Player quote: 「感覺系統想讓我答對」
* 設計問題: phase 2 決定是 feature 或 bug
* Source: Multiple testing sessions

### 🟢 待 phase 2 設計重構

#### F7: 缺風味動作 support

* Symptom: 玩家嘗試 purely roleplay actions 被拒絕
* Player quote: 「自由度還行但有些動作不被允許」
* 修法: narration-only response support
* Source: Engineer Tester

#### F8: Rule Enforcer 應分嚴格/寬鬆兩層

* Player insight: 不影響 puzzle progression 的行為應該允許
* 設計方向:

  * Layer 1: puzzle-critical actions
  * Layer 2: flavor actions
* Source: Engineer Tester

#### F9: Puzzle 類型單一

* Symptom: 玩家發現 puzzle pattern 過度偏向 fetch quest
* Player quote: 「很多題目本質都像在 A 拿東西放到 B」
* 修法: 增加 puzzle type diversity
* Source: Engineer Tester

### F10: Channel collision (多玩家訊息混雜)

* Symptom: 多玩家在同 channel 遊玩時互相看到 narration/hints
* 影響:

  * spoiler
  * immersion break
  * visual noise
* 修法方向:

  * private thread per player
  * DM mode
* Source: Real multi-user testing

### F11: 「值得分享 moment」缺乏系統性設計

* Symptom: viral moments 目前多半是 accidental
* 目標: 每場至少 1-3 個 memorable/shareable moments
* 設計方向:

  * impossible action reactions
  * hidden item personalities
  * occasional fourth-wall breaks
  * bizarre failure narration
* 優先級: HIGH
* Source: Emergent player behavior analysis

### F12: 玩家行為 metric tracking

* 目的: 理解卡關率、通關率、回鍋率
* 要追蹤:

  * stagnant turn streak
  * return rate
  * completion rate
* 不追蹤:

  * raw player messages
  * detailed conversation logs
* Source: Internal analytics planning

### F13: Weird moment counting

* Why: weird moments 是最直接的 shareability metric
* 實作:

  * TurnResult 增加 is_weird_moment
  * 自動標記 surreal / fourth-wall / personality moments
* 用途: 提升 weird moment density

### F14: Non-linear puzzle chain

* 現況: 線性 chain 已可運作
* 進階: interconnected puzzle dependency
* 問題: 目前 LLM planning stability 不足
* 優先級: LOW

---

## Phase 1.5

### Per-user daily scenario limit

* Trigger: 高 engagement tester 單日消耗遠高於預期
* 修法: 每日 scenario 上限

### OAuth invite URL permissions 修正

* 補齊 bot permissions

### Narration tone 漏網修正

* 避免過度文藝化 narration

### 通關後 session handling

* 通關後引導玩家開始新遊戲

### Onboarding 補完

* guild join handler
* mention handler
* unknown command fallback

### Escape N spam 處理

* 防止重複 generation request

---

## Phase 2

### Web UI + FastAPI backend

* 降低 Discord friction

### SQLite + LiteFS

* 取代 JSON files

### 結局分享卡

* 通關後產生 shareable image

### 視覺化 inventory + map

* icon inventory
* mini-map

### Rate limit middleware

* per-user / per-IP control

---

## Phase 3+

### Theme: 考古探索

* 共用 engine
* 改 prompt layer

### Theme: 偵探推理

* NPC interactions
* evidence system

### Narrative Director

* 第三層 storytelling LLM
* 動態調整 narration tone

### Per-player Discord thread

* 降低 channel collision

### Admin-only cleanup commands

* moderation protection

---

## Out of scope

* ❌ Multi-player co-op
* ❌ Mobile native app
* ❌ Pure NPC simulation
* ❌ Pure visual novel mode
* ❌ Specialized professional simulations
* ❌ Early over-engineering of retention systems

核心原則:

* 不靠 addictive loop retention
* 靠「值得分享」與 emergent moments 成長

---

## Deploy lessons learned

### `.dockerignore` 必須包含 `.venv/`

* 避免 local virtualenv 污染 container

### Fly.io machine restart issue

* max restart count 導致 stopped state

### `.env` 不應進 image

* production 使用 secrets

### Docker CMD 使用絕對路徑

* 避免 system python mismatch

### deploy 時必要時使用 `--no-cache`

* 避免 stale Docker layer

### Player session data 不應進 git

* 包含:

  * puzzle spoilers
  * player conversations
  * analytics metadata
  * identifiable usernames

---

## Cost monitoring

### Ship day observations

High-engagement tester:

* 真實成本遠高於初始估算
* 原因: 玩家不是「玩到通關」, 而是「玩到滿足」

修正後 projection:

* 一般玩家: low-to-moderate cost
* High-engagement players: significantly higher daily usage
* Public release: 必須加 rate limiting + spend cap

Mitigation:

* monthly spend cap
* per-user scenario limit
* middleware rate limiting
