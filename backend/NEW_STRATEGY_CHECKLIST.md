# New Strategy Checklist (AI + Human)

Use this checklist every time you add a strategy (for example: `cdm`).

## 1) Backend runtime strategy

1. Create `backend/strategies/<strategy>_strategy.py`.
2. Inherit `BaseStrategy` and implement:
   - `calculate_plan(**kwargs)` (return `allocation_weights` and optional metadata)
   - `get_parameters()` (UI input schema)
3. Keep `allocation_weights` positive and normalized to ~1.0.
4. Return stable, explicit error messages as `{"error": "..."}`.

## 2) Register strategy API visibility

1. Add import + registry entry in `backend/strategies/__init__.py`.
2. Confirm `/api/strategies` exposes correct:
   - `name`
   - `description`
   - `parameters`

## 3) Cache key normalization (important)

1. Update `backend/cache/keys.py` in `_canonical_parameters(...)` for the new strategy id.
2. Normalize list-like parameters (tickers):
   - trim
   - uppercase
   - deduplicate
   - sort
3. Normalize numeric params (`"12"` and `12` should map to one cache key).
4. Goal: semantically identical inputs must hit the same cache entry.

## 4) Performance backtest integration

1. Add `backend/performance/specs/<strategy>.py` with `StrategyPerformanceSpec`.
2. Implement:
   - `default_parameters()`
   - `normalize_parameters()`
   - `universe()`
   - `compute_weights(history, parameters)`
3. Register in `backend/performance/specs/__init__.py`.
4. Ensure `compute_weights` is pure:
   - no network I/O
   - no DynamoDB calls
   - use only passed `history`

## 5) Frontend parameter handling

1. If custom UI needed, add panel in `src/strategies/panels/` and wire in `src/strategies/registry.js`.
2. If generic panel is enough, verify parameter names/types from backend are sufficient.
3. Validate array/text parameter parsing in the caller path (dashboard/selector).

## 6) Strategy education + localization

1. Add education block to:
   - `src/data/strategyEducation.js` (English)
   - Korean path used by the app (current code mixes `translations.js` and education data)
2. Add strategy display text in `src/i18n/translations.js`:
   - `translations.en.strategies.<id>`
   - `translations.ko.strategies.<id>`
3. Save file as UTF-8 to avoid Korean mojibake.

## 7) Data and numerical behavior

1. Define lookback windows and required minimum history explicitly.
2. Handle missing tickers/data gracefully; include `missing_tickers` where useful.
3. Keep rebalance cadence consistent (monthly in this project unless intentionally different).
4. Include deterministic tie-break rules (for equal momentum/scores).

## 8) API compatibility contract

1. `calculate_plan()` output should include `allocation_weights`.
2. Optional metadata keys are safe, but avoid breaking existing keys consumed by UI.
3. Errors should be user-readable and actionable.

## 9) Verification before merge

1. Smoke test:
   - `GET /api/strategies`
   - `POST /api/calculate` with default params
   - `GET /api/performance?strategy_id=<id>`
2. Confirm cache behavior:
   - second identical request should return cached plan path.
3. Confirm UI:
   - strategy visible
   - parameter form renders
   - results + education copy display in EN/KO

## 10) Deployment note

If your deployment packages backend code into a separate artifact directory (for example `backend/lambda_pkg`), ensure the new strategy and spec are included in that artifact build.
