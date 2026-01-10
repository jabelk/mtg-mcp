# Implementation Plan: Scryfall API Integration

> **What is this file?** This is the *implementation plan* - it describes HOW we'll build the feature defined in `01-spec-scryfall-integration.md`. Now we make technical decisions.

---

## Prerequisites

- [x] Spec complete with all clarifications resolved
- [ ] Understand current code structure
- [ ] Identify what needs to change

---

## Current State Analysis

**File:** `src/tools/card_lookup.py`

```python
# Current fake implementation:
async def lookup(name: str) -> dict:
    # Only returns data for "atraxa"
    # Raises FakeCardLookupError otherwise
```

**What we keep:**
- Function signature: `async def lookup(name: str) -> dict`
- Return schema (6 fields)
- Error handling pattern (raise exception for not-found)

**What we change:**
- Replace hardcoded response with HTTP call to Scryfall
- Add new exception type for service unavailable

---

## Technical Decisions

### HTTP Library Choice

**Options:**
1. `httpx` - Modern async HTTP, recommended for new Python projects
2. `aiohttp` - Also async, more mature but heavier
3. `requests` - Sync only, would need threading

**Decision:** `httpx` - async-native, simple API, lightweight

### Field Mapping

Scryfall field → Our field:
```
name          → name
type_line     → type_line
oracle_text   → oracle_text
cmc           → mana_value
image_uris.small → image_small
rulings_uri   → rulings_uri
```

**Note on double-faced cards:** Scryfall uses `card_faces` array instead of top-level fields. We'll check for this and use `card_faces[0]` (front face).

---

## Implementation Steps

### Step 1: Add httpx dependency
```bash
pip install httpx
# Update requirements.txt
```

### Step 2: Update card_lookup.py

1. Add new exception class: `CardLookupError` (replaces `FakeCardLookupError`)
   - Include error type: `not_found` | `service_unavailable`

2. Rewrite `lookup()` function:
   - Make HTTP GET to Scryfall
   - Handle 404 → raise not_found
   - Handle connection error → raise service_unavailable
   - Parse response and map fields
   - Handle double-faced cards (use front face)

### Step 3: Update server.py

1. Update import (new exception class name)
2. Add handler for `service_unavailable` error type

### Step 4: Test manually

```bash
# Run the server
python src/server.py

# Or test the lookup directly in Python REPL
```

---

## Error Handling Matrix

| Scenario | Scryfall Response | Our Response |
|----------|------------------|--------------|
| Card found | 200 + JSON | Return mapped fields |
| Card not found | 404 | `{"error": "not_found", ...}` |
| Bad request | 400 | `{"error": "not_found", ...}` |
| Scryfall down | Connection error | `{"error": "service_unavailable", ...}` |
| Scryfall 500 | 500 | `{"error": "service_unavailable", ...}` |

---

## Testing Checklist

After implementation, test these cases:

- [ ] `"Black Lotus"` → returns correct card
- [ ] `"blck ltus"` → fuzzy match works
- [ ] `"Delver of Secrets"` → double-faced card, returns front face
- [ ] `"xyznotacard123"` → returns not_found error
- [ ] (manually break URL) → returns service_unavailable error

---

## Rollback Plan

If something goes wrong:
- Git revert to previous commit
- Original fake implementation is preserved in git history

---

## Learning Notes

**Why write a plan before coding?**

1. **Surface unknowns** - The double-faced card issue came up during planning, not mid-implementation
2. **Make decisions explicit** - "Why httpx?" is documented, not buried in code
3. **Create a checklist** - Implementation steps are clear, nothing forgotten
4. **Enable review** - Someone could review this plan before any code is written

**Spec vs Plan:**
- Spec = WHAT (requirements, user stories, success criteria)
- Plan = HOW (technical decisions, architecture, steps)
