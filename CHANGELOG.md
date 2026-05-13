# Changelog

## v1.0.1 (2026-05-13) - Phase 1.5 hotfix

### Fixed
- Puzzle solution format normalization: bot now parses fuzzy player input 
  and confirms format before submission
- Hint request handling: bot gives in-character guidance instead of 
  refusing or repeating clues
- Player session persistence: data now stored on fly volume, survives 
  deploy and machine restarts

### Infrastructure
- Add fly volume `escape_data` (1GB) mounted at `/app/User`
- `.dockerignore` excludes runtime player data

## v1.0.0 (2026-05-12) - Phase 1 ship

### Added
- LLM-driven scenario generation (Gemini 2.5 Pro/Flash)
- Free-text Discord interaction with Pydantic-validated state
- Traditional Chinese narration
- Anti-injection multi-layer defense
- Persistent session storage (escape L resume)
- First-time player onboarding