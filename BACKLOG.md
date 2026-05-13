# EscapeBot Backlog

## Phase 1 findings

從 manual test + production 真實玩家撞牆 surface 的 issues。

### 🔴 High priority

#### F15: Puzzle solution format ambiguity
- **Symptom**: 玩家有正確線索但不知道輸入格式
  - 嘗試多種組合（不同順序 / 分隔 / 大小寫）皆被 reject
  - 同一個 puzzle 連續嘗試 10+ 次仍 fail
- **Cost impact**: 每次 fail = 3x retry LLM call
- **修法 (按工作量排序)**:
  - **Tier 1 (prompt)**: Turn Handler 解析玩家 fuzzy input，轉成 expected format
  - **Tier 2 (schema)**: Scenario Generator 強制 intuitive solution format + description 明確 format hint
  - **Tier 3 (engine)**: Rule Enforcer 接受 partial match，narrate「快了，但不完全對」

#### F-hint: Hint request handling
- **Symptom**: 玩家 in-game 問「X 是什麼意思」/「下一步呢」時，bot 重複描述線索或拒絕，沒給暗示
- **原因**: anti-injection rules over-kill 合理 hint request
- **修法**: Turn Handler prompt 區分「玩家求 hint」vs「玩家試圖 hack」
  - 前者：in-character 給暗示，不直接 spoil
  - 後者：維持 anti-injection 拒絕

### 🟡 Medium priority

#### F1: Puzzle 解開瞬間 narration 信號不明確
- **Symptom**: 正確 attempted_solution 後 narration 沒明確說「解開了」
- **修法**: Turn Handler prompt 強化 success signaling

#### F2: 玩家在錯誤 location 嘗試 puzzle solution 沒引導
- **Symptom**: Bot reject 但不告訴玩家「該回 X 房間」
- **修法**: Rule Enforcer reject 時加 hint 給 LLM

#### F5: 缺 drop_item action type
- **Symptom**: 玩家試圖丟棄物品時，schema 沒對應 action，LLM 用超現實 narration 拒絕
- **評估**: 偶爾變 share-worthy moment，但長期該修
- **修法**: StateChange 加 drop_item type

#### F9: Puzzle 類型單一 (主要是 fetch quest)
- **Symptom**: 多場後玩家看穿 puzzle pattern 重複
- **修法**: Scenario Generator prompt 強制每場 ≥2 種 puzzle types
- **Types**: fetch quest / code derivation / sequence / combination / observation / logic

#### F11: 「值得分享」moment 缺乏系統性設計
- **目標**: 每場至少 1-3 個 viral-worthy moment（不靠 bug 副作用）
- **4 種設計方向** (詳細 spec 在 notes/JOURNAL.md):
  - Type A: 不可能動作的 in-character 詭異接受
  - Type B: 物品 hidden personality
  - Type C: 4th wall 偶爾打破
  - Type D: 詭異 failure narration
- **配套 metric F13**: weird moment count tracking

#### F16: Multi-hop movement not supported
- **Symptom**: 玩家打「走回 A 再走到 B」(經過多個 location) → engine 只支援單 hop reject
- **修法**:
  - Tier 1 (prompt): Turn Handler narrate 中間經過, state 一次 1 hop
  - Tier 2 (engine): Rule Enforcer 支援 multi-hop chain

### 🟢 Low priority

#### F3: 環境線索沒有持久化
- **Symptom**: 玩家早期看到的線索後續忘記，無 inventory/note 記錄
- **修法**: phase 2 加玩家筆記本，或 prompt 在 state query 時 surface 線索

#### F4: 救援機制存在但不明確
- **Symptom**: 玩家亂試後 narration 出現「鎖頭其實鬆動」這類 fallback hint
- **設計問題**: 是 feature 還是 bug 待決定

#### F13: Weird moment count metric
- **目的**: 「詭異瞬間數」是 share-worthiness leading metric
- **實作**: TurnResult schema 加 is_weird_moment field, LLM 自標
- **配合 F11**

### 待 phase 2 重構

#### F7: 缺風味動作 support
- **Symptom**: 玩家試「穿衣服」「對物品唱歌」等非 puzzle 動作被拒
- **修法**: Turn Handler 允許 narration-only response (state_changes=[], 但認真演)

#### F8: Rule Enforcer 該分嚴格/寬鬆兩層
- **設計**:
  - Layer 1 (嚴格): 影響 puzzle/win 的動作 → 嚴格驗證
  - Layer 2 (寬鬆): 純風味動作 → LLM 自由 narration, state 不變

#### F14: Non-linear puzzle chain
- **現況**: 已支援線性 chain
- **進階**: Puzzle 間 interconnected (e.g. puzzle 1 解答暗示 puzzle 3)
- **延後**: 需要更強 LLM planning

---

## Phase 1.5

修 phase 1 surface 的 issues, ship 給更多玩家前該做。

- **Per-user daily scenario limit** (cost mitigation)
- **OAuth invite URL 補 Manage Messages + Use External Emojis 權限**
- **Narration tone 漏網修正** (偶爾仍生文藝句)
- **通關後玩家輸入處理** (待測試)
- **Onboarding 補完** (on_guild_join / mention handler / unknown command fallback)
- **Escape N spam dedup**

---

## Phase 2

Web 版規劃。觸發條件: 累積真實 friction 證據顯示 Discord 是 blocker。

- Web UI + FastAPI backend
- SQLite + LiteFS 取代 JSON files
- 結局分享卡 (PNG generation)
- 視覺化 inventory + map
- Rate limit middleware

---

## Phase 3+

- **Theme: 考古探索** (跟逃脫共用 engine, 改 prompt, 1-2 天)
- **Theme: 偵探推理 / 找兇手** (加 NPC model, 3-5 天)
- **Narrative Director** (第三層 LLM 動態調整 narration tone)
- **Per-player Discord thread** (避免 channel collision)
- **`/clean` 限制 admin**

---

## Out of scope

- Multi-player co-op
- Mobile native app
- 純 NPC 對話模擬
- 純 narrative / visual novel
- 醫療 / 法律專業模擬
- 多 LLM provider fallback
- Personalized AI (記住玩家偏好)
- Retention reward (streak / badge) — 違反 「值得分享」success metric

---

## Deploy lessons learned

工程坑 + 解法。

### `.dockerignore` 必須有 `.venv/`
- `COPY . .` 會把本地 .venv 蓋掉 builder 的 .venv
- 本地 macOS .venv 在 Linux container 跑不了
- 防護: Dockerfile 加 venv sanity check

### Fly.io machine stuck in `stopped` after deploy
- 撞 max restart count (10) → machine 停
- 解法: `flyctl machine start <machine_id>`

### `.env` 不該進 Docker image
- 加 `.env` 到 `.dockerignore`, production 走 fly secrets

### Fly.io high-risk-unlock 是 normal flow
- Legacy hobby plan dormant → active 易觸發, 填表 + 加信用卡解

### Dockerfile CMD 用絕對路徑
- `CMD ["/app/.venv/bin/python", "bot.py"]` 保證走 venv

### Fly.io deploy 用 `--no-cache`
- 改 Dockerfile / base image 後 fly cache 可能不更新

### Player session data 不該進 git
- `User/users/` 加 `.gitignore`

---

## Cost monitoring

### 2026-05-12 (ship day) - REAL DATA

**Viral player playthrough**:
- 3 sessions, 262 total turns (105 + 37 + 120)
- 真實帳單: NT$141.99 (~$4.6 USD)
- vs 預估 $1.20 = 3.8x 高
- Per-turn cost: ~$0.018

**Projection (revised)**:
- 一般玩家 (one playthrough ~50-80 turns): ~$1-1.5
- Viral player (3 sessions ~200 turns): $3-5
- 5 朋友混合: ~$15/月 (在 budget 內)

**Safety net**:
- Google AI Studio cap: $30/month (硬上限)