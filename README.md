# EscapeBot

LLM 驅動的 Discord 文字逃脫遊戲機器人。每場遊戲的場景、物品、謎題都由 Gemini 即時生成，全程繁體中文，支援自然語言互動。

> ⚠️ 個人 hobby 專案 (non-profit)。請勿用於大型 server 或正式社群。

## 邀請 Bot

[點此邀請到你的 Discord server](https://discord.com/api/oauth2/authorize?client_id=861144762358169626&permissions=59392&scope=bot)

## 怎麼玩

加入 server 後，在任意 channel 輸入以下指令：

| 指令 | 功能 |
| --- | --- |
| `escape N` | 開新場景 (生成需 30-60 秒) |
| `escape L` | 載入上次進度 |
| `escape H` | 完整指南 |
| `q` | 暫停遊戲 (進度保留，可隨時 escape L 繼續) |
| `clear {num}` | 清除頻道 {num} 則訊息 |

開新場景後，用自由文字描述你想做什麼，例如：

- `看看四周`
- `拿起鑰匙`
- `移動到走廊`
- `仔細查看書本`
- `輸入 1234`

不需要記固定指令，bot 會理解你的意圖。

## 技術架構

- **Discord Bot**: discord.py
- **LLM**: Google Gemini (gemini-2.5-pro 生成場景, gemini-2.5-flash 處理回合)
- **State management**: Python + Pydantic + Rule Enforcer (LLM 不能跳過解謎、無法憑空產生物品)
- **Deployment**: Fly.io (multi-stage Docker with uv)
- **Dependency management**: uv

## 為什麼是 LLM 驅動

傳統文字冒險遊戲的場景是寫死的，玩過一次就沒新鮮感。EscapeBot 每次 `escape N` 由 LLM 即時生成完整的場景結構（3-5 個房間、4-8 個物品、2-3 個謎題），確保每場都不同但仍然可通關。

Python 端維護 World State 作為 ground truth，LLM 只能在合法範圍內改變狀態。玩家試圖透過 prompt injection 或想像物品來作弊都會被擋下。

## 開發

詳見 [DEVELOPMENT.md](DEVELOPMENT.md)。簡要：

```bash
uv sync
uv run pytest
uv run python bot.py
```

## Version log

- **v1.0** (2026-05-12): LLM-driven 場景生成。Gemini 2.5 Pro/Flash，free-text 互動，繁體中文敘事，Rule Enforcer 防作弊，anti-injection 防越獄
- v0.5 (2023-01-26): English version (deprecated)
- v0.4: Discord API 2.0 升級
- v0.3.x: 多玩家支援、24/7 deploy、clear command
- v0.2: Record system + bug fix
- v0.1: 初版 Level 1
