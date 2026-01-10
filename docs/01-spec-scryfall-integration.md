# Spec: Scryfall API Integration

> **What is this file?** This is a *specification* - it describes WHAT we want to build, not HOW to build it. The key principle of spec-driven development is separating requirements from implementation.

---

## Feature Overview

**Feature Name:** Real Scryfall Card Lookup
**Status:** Draft
**Date:** 2025-01-09

### Problem Statement

The current `mtg_card_lookup` tool only returns fake/hardcoded data for cards containing "atraxa". Users need to look up any Magic: The Gathering card by name.

### User Story

> As a user of the MTG MCP server,
> I want to look up any Magic card by name,
> So that I can get accurate card information (text, mana cost, image, etc.)

---

## Success Criteria

> **Spec-Driven Principle:** Success criteria should be *testable* and *technology-agnostic*.
> - Bad: "Use httpx library" (that's implementation)
> - Good: "Returns card data within 2 seconds" (that's testable behavior)

1. **Fuzzy matching works** - Searching "black lotus" returns "Black Lotus" even with imperfect spelling
2. **Returns consistent schema** - Response includes: name, type_line, oracle_text, mana_value, image URL
3. **Handles not-found gracefully** - Invalid card names return a helpful error, not a crash
4. **Reasonable performance** - Responses return within 3 seconds under normal conditions

---

## Scope

### In Scope
- Replace fake lookup with real Scryfall API call
- Maintain existing response schema (don't break the interface)
- Handle API errors gracefully

### Out of Scope (for now)
- Caching responses
- Rate limiting
- Advanced search (by set, color, etc.)
- Multiple card results (autocomplete)

---

## Questions / Clarifications Needed

> **Spec-Driven Principle:** It's okay to have unknowns! Mark them clearly. Resolve before implementation.

1. [x] What fields from Scryfall do we actually need? (Scryfall returns ~50+ fields)
   - **Decision:** Keep existing 6 fields: `name`, `type_line`, `oracle_text`, `mana_value`, `image_small`, `rulings_uri`
   - **Rationale:** Maintains backward compatibility with current interface

2. [x] Should we handle double-faced cards specially?
   - **Decision:** Front face only for now
   - **Rationale:** Keeps scope tight. Double-faced cards (werewolves, MDFCs, transform cards) are increasing in frequency but not needed for v1
   - **Future:** Could add `back_face` field or separate tool later

3. [x] What happens if Scryfall is down?
   - **Decision:** Return error dict with `"error": "service_unavailable"`
   - **Rationale:** Consistent with existing `"error": "not_found"` pattern

---

## API Reference

Scryfall's named card endpoint:
```
GET https://api.scryfall.com/cards/named?fuzzy={card_name}
```

Example response fields we care about:
- `name` - Card name
- `type_line` - "Legendary Creature — Human Wizard"
- `oracle_text` - Rules text
- `cmc` - Converted mana cost (mana_value)
- `image_uris.small` - Small image URL
- `scryfall_uri` - Link to full card page

---

## Next Steps

1. Answer the clarification questions above
2. Write implementation plan (see `02-plan-*.md`)
3. Implement and test

---

## Learning Notes

**Why write a spec first?**

1. **Forces clarity** - You can't implement what you don't understand
2. **Catches scope creep** - "Out of Scope" section prevents feature bloat
3. **Enables review** - Others (or AI) can review the spec before you write code
4. **Creates documentation** - This file becomes reference material

**Key spec-driven principles used here:**
- WHAT not HOW (no code, no library choices)
- Testable success criteria
- Explicit scope boundaries
- Acknowledged unknowns
